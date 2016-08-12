import os
import fnmatch
import json
import io
from flask import (Flask, request, render_template, redirect, url_for,
    flash, jsonify, abort)
from apscheduler.schedulers.background import BackgroundScheduler
from flask.ext.cache import Cache
from resources.api_data import csv_api
from celery import Celery

# Server config
#import sys
#sys.path.append('/etc/')

# Our Scripts
import generator
import data_manager
import repo_manager
import stash_api
import settings

app = Flask(__name__)
app.register_blueprint(csv_api)
secret = os.urandom(24)
app.secret_key = secret

app.config['CACHE_TYPE'] = 'simple'
app.cache = Cache(app)

celery = Celery(app.name, backend=settings.RESULT_BACKEND,
                broker=settings.BROKER_URL)

maat_dir = settings.maat_dir
repo_dir = settings.repo_dir
csv_dir = settings.csv_dir
list_of_projects = stash_api.get_projects()
generator.set_path(maat_dir)

clone_sched = BackgroundScheduler()
clone_sched.add_job(lambda: repo_manager.refresh_repos(repo_dir),
                    'cron', day='0-6', hour='1')
clone_sched.start()


# homepage where user can select/add a repository to begin analysis process
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', list_of_projects=list_of_projects)
    elif request.method == 'POST':
        proj_key = request.form.get('proj_key', '', type=str)
        repo_name = request.form.get('repo_name', '', type=str).lower()
        from_date = request.form.get('from_date', '', type=str)
        to_date = request.form.get('to_date', '', type=str)

        if generator.bad_range(from_date, to_date):
            flash("Sorry. There was a problem with your date range.")
            return redirect(url_for('index', list_of_projects=list_of_projects))
        elif generator.analysis_exists(repo_name, from_date, to_date):
            return redirect(url_for('dashboard', repo_name=repo_name,
                from_date=from_date, to_date=to_date, location='NULL'))
        else:
            task = run_analysis.delay(repo_name, proj_key, from_date, to_date)
            return redirect(url_for('dashboard', repo_name=repo_name,
                from_date=from_date, to_date=to_date,
                location=url_for('taskstatus', task_id=task.id)))


# Status route for task status retrieval
@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = run_analysis.AsyncResult(task_id)
    response = {'state': task.state}
    return jsonify(response)


# Asyncronous task (clone and run analysis)
@celery.task(bind=True)
def run_analysis(self, repo_name, proj_key, from_date, to_date):
    self.update_state(state="CLONING")
    repo_manager.repo_check_and_update(repo_name, proj_key, to_date, self)
    self.update_state(state="ANALYZING")
    generator.manage_csv_folder(repo_name, from_date, to_date, self)
    return (repo_name, from_date, to_date)


@app.route('/_return_repos')
def return_repos():
    return_val = ''
    key = request.args.get('key', '', type=str)
    repos = stash_api.get_project_repos(key, 'http', '100')
    for repo in repos:
        return_val += ('<option value="' + repo['name'] + '">' +
                       repo['name'] + '</option>')
    return jsonify(result=return_val)


@app.route('/_return_repo_dates')
def return_repo():
    key = request.args.get('key', '', type=str)
    name = request.args.get('name', '', type=str)
    if key == '' or name == '':
        return jsonify(null='api call did not return anything')
    dates = stash_api.get_repo_timestamp(key, name, '15000')
    return jsonify(result=dates)


# page where user can select the specific analysis to view
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    repo_name = request.args.get('repo_name')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    location = request.args.get('location')
    if request.method == 'GET':
        # buttons to all analyses available; assumed all have been run
        return render_template('input.html', location=location)
    elif request.method == 'POST':
        analysis = request.form.get('analysis', '', type=str)
        return redirect(url_for('result',
            repo_name=repo_name, analysis=analysis,
            from_date=from_date, to_date=to_date))


@app.cache.memoize(timeout=60 * 60)
def get_csv_data(path, filename):
    return data_manager.parse_csv(path, filename)


@app.cache.memoize(timeout=60 * 60)
def get_log_data(path, filename):
    return data_manager.get_word_frequency(path, filename)


# page where user can view the visualized data
@app.route('/result', methods=['GET', 'POST'])
def result():
    repo_name = request.args.get('repo_name')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    if request.method == 'GET':
        analysis = request.args.get('analysis')
        if not repo_name or not analysis or not from_date or not to_date:
            abort(404)
        repo_details = repo_name + "_" + from_date + "_" + to_date
        if analysis == "cloud":
            data, keys = get_log_data(os.path.join(csv_dir, repo_details),
                analysis + "_" + repo_details + ".log")
        else:
            data, keys = get_csv_data(os.path.join(csv_dir, repo_details),
                analysis + "_" + repo_name + ".csv")
        if data == []:
            if analysis == 'coupling':
                flash('Congratulations! No coupling detected.')
                return redirect(url_for('dashboard',
                    repo_name=repo_name, from_date=from_date, to_date=to_date))
            abort(404)
        return render_template('result.html',
            repo_name=json.dumps(repo_name), analysis=json.dumps(analysis),
            from_date=from_date, to_date=to_date,
            data=json.dumps(data), keys=json.dumps(keys))
    elif request.method == 'POST':
        analysis = request.form.get('analysis', '', type=str)
        return redirect(url_for('result',
            repo_name=repo_name, analysis=analysis,
            from_date=from_date, to_date=to_date))


# this filter allows using '|fromjson' in a jinja template
# to call json.loads() method
@app.template_filter('fromjson')
def convert_json(s):
    return json.loads(s)


# customized error page
@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html')


# customized error page
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')

if __name__ == '__main__':
    app.run(debug=settings.DEBUG_MODE)
