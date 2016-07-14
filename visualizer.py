import os
import fnmatch
import json
import io
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import generator # our script
import stash_api # our script
import settings # our script
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.contrib.cache import SimpleCache
# from datetime import datetime

app = Flask(__name__)
secret = os.urandom(24)
app.secret_key = secret

cache = SimpleCache()

maat_dir = settings.maat_dir # address of codemaat
repo_dir = settings.repo_dir # address of cloned repositories
csv_dir = settings.csv_dir # address of csv folders
list_of_projects = stash_api.get_projects() # list of projects on Stash
generator.set_path(maat_dir) # set path for codemaat

clone_sched = BackgroundScheduler() # configuration for apscheduler
clone_sched.add_job(lambda:generator.refresh_repos(),
				 'cron', day='0-6', hour='1')
# clone_sched.add_job(lambda:generator.refresh_repos(),
					# 'interval', hours=2)
	# lambda passes function as parameter
	# cron is a configuration for time schedules
	# configured for everyday of week (0-6), at 12 AM (0)
clone_sched.start()


# homepage where user can select/add a repository to begin analysis process
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('index.html', list_of_projects=list_of_projects)
	elif request.method == 'POST':
		if request.form.get('submit_button', '', type=str) == "run_analysis":
			proj_key = request.form.get('proj_key', '', type=str)
			repo_name = request.form.get('repo_name', '', type=str).lower()
			from_date = request.form.get('from_date', '', type=str)
			to_date = request.form.get('to_date', '', type=str)

			generator.repo_check_and_update(repo_name, proj_key, to_date)

			if not generator.manage_csv_folder(repo_name, from_date, to_date):
				flash('No data for selected date range found.')
				return redirect(url_for('index'))
			else:
				return redirect(url_for('dashboard',
					repo_name=repo_name, from_date=from_date, to_date=to_date))
					# redirects to dashboard view which opens input.html
		elif request.form['submit_button'] == "clone":
			# if user provided a clone url and password
			clone_url = request.form['clone_url']
			password = request.form['password']
			generator.clone_repo(clone_url, password) # go to repo_dir and clone the repo
			# message = generator.get_status_message(clone_url)
			# flash(message) # displays a confirmation message on the screen
			return redirect(url_for('index'))
		else:
			# if a selection was made from 'Stash Repositories'
			project_name = request.form['submit_button']
			return redirect(url_for('index_repo', project_name=project_name))

@app.route('/_return_repos')
def return_repos():
	return_val = ''
	key = request.args.get('key', '', type=str)
	repos = stash_api.get_project_repos(key,'http')
	for repo in repos:
		return_val += '<option value="'+repo['name']+'">'+repo['name']+'</option>'
	return jsonify(result=return_val)

@app.route('/_return_repo_dates')
def return_repo():
	key = request.args.get('key', '', type=str)
	name = request.args.get('name', '', type=str)
	dates = stash_api.get_repo_timestamp(key, name, 'http', '15000')
	return jsonify(result=dates)

# page where user can select a repository after selecting a Stash project
@app.route('/index_repo', methods=['GET', 'POST'])
def index_repo():
	# retrieves passed in query from index view
	project_name = request.args.get('project_name')
	project_repos = stash_api.get_project_repos(project_name, 'http')
		# dictionary of repos in Stash belong to selected project

	if request.method == 'GET':
		# previous_date = generator.get_prev_date()
		# current_date = str(datetime.now()).split('.')[0].split(' ')[0]
		return render_template('index_repo.html', repo_list=project_repos)
	elif request.method == 'POST' and not request.form['repo_name'] == "":
		selected_repo = request.form['repo_name'].split('|')
		repo_name = selected_repo[0].lower()
		repo_url = selected_repo[1] # string: clone url
		from_date = request.form['from_date']
		to_date = request.form['to_date']
		generator.clone_repo(repo_url, settings.password) # go to repo_dir and clone the repo
		generator.manage_csv_folder(repo_name, from_date, to_date)
		return redirect(url_for('dashboard',
			repo_name=repo_name, from_date=from_date, to_date=to_date))
			# go straight to dashboard after cloning repo and generating files

# page where user can select the specific analysis to view
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	# retrieves passed in queries from index view
	repo_name = request.args.get('repo_name')
	from_date = request.args.get('from_date')
	to_date = request.args.get('to_date')

	if request.method == 'GET':
		# buttons to all analyses available; assumed all have been run
		return render_template('input.html')
	elif request.method == 'POST':
		analysis = request.form['analysis']
		return redirect(url_for('result',
			repo_name=repo_name, analysis=analysis,
			from_date=from_date, to_date=to_date))


# page where user can view the visualized data
@app.route('/result', methods=['GET', 'POST'])
def result():
	# retrieves passed in queries from dashboard view
	repo_name = request.args.get('repo_name')
	analysis = request.args.get('analysis')
	from_date = request.args.get('from_date')
	to_date = request.args.get('to_date')

	repo_details = repo_name + "_" + from_date + "_" + to_date

	if request.method == 'GET':
		if analysis == "cloud":
			try:
				with open(csv_dir + repo_details + "/"
					+ analysis + "_" + repo_details + ".log", 'rt') as log_file:
					word_list = cache.get('cloud_' + repo_details)
					if word_list is None:
						word_list = generator.get_word_frequency(log_file)
						cache.set('cloud_' + repo_details,
							word_list, timeout=60 * 60)
				return render_template('result.html',
					data=word_list, repo_name=json.dumps(repo_name),
					analysis=json.dumps(analysis),
					from_date=from_date, to_date=to_date, keys=[])
			except UnicodeError:
				with io.open(csv_dir + repo_details + "/"
					+ analysis + "_" + repo_details
					+ ".log", 'rt', encoding='utf-8') as log_file:
					word_list = cache.get('cloud_' + repo_details)
					if word_list is None:
						word_list = generator.get_word_frequency(log_file)
						cache.set('cloud_' + repo_details,
							word_list, timeout=60 * 60)
				return render_template('result.html',
					data=word_list, repo_name=json.dumps(repo_name),
					analysis=json.dumps(analysis),
					from_date=from_date, to_date=to_date, keys=[])
			except (FileNotFoundError, IOError):
				return render_template('404.html')
		else:
			try:
				with open(csv_dir + repo_details + "/"
					+ analysis + "_" + repo_name + ".csv", 'rt') as csv_file:
					data = cache.get('data_' + analysis + '_' + repo_details)
					keys = cache.get('keys_' + analysis + '_' + repo_details)
					if data is None:
						data, keys = generator.parse_csv(csv_file)
						cache.set('data_' + analysis + '_' + repo_details,
							data, timeout=60 * 60)
						cache.set('keys_' + analysis + '_' + repo_details,
							keys, timeout=60 * 60)
					return render_template('result.html',
						repo_name=json.dumps(repo_name), analysis=json.dumps(analysis),
						from_date=from_date, to_date=to_date,
						data=json.dumps(data), keys=json.dumps(keys))
							# json.dumps() converts data into a string format
			except (FileNotFoundError, IOError):
				return render_template('404.html')
	elif request.method == 'POST':
		analysis = request.form['analysis']
		return redirect(url_for('result',
			repo_name=repo_name, analysis=analysis,
			from_date=from_date, to_date=to_date))

# this filter allows using '|fromjson' in a jinja template
# to call json.loads() method
@app.template_filter('fromjson')
def convert_json(s):
	return json.loads(s)

# customized error page
@app.errorhandler(404)
def not_found(e):
	return render_template ('404.html')

# customized error page
@app.errorhandler(400)
def bad_request(e):
	return render_template ('400.html')


if __name__ == '__main__':
	app.run(debug=True)
	# app.run()
