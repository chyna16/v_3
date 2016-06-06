import os
import fnmatch
import json
from flask import Flask, request, render_template, redirect, url_for, flash
import generator # our script
import stash_api # our script
import settings # our script
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
secret = os.urandom(24)
app.secret_key = secret

maat_dir = settings.maat_directory # address of codemaat
repo_dir = settings.repo_directory # address of cloned repositories
list_of_projects = stash_api.get_projects() # list of projects on Stash
generator.set_path(maat_dir) # set path for codemaat
# generator.clone_repos(repo_dir, settings.password)

clone_sched = BackgroundScheduler() # configuration for apscheduler
clone_sched.add_job(lambda:generator.clone_repos(repo_dir, settings.password),
				 'cron', day='0-6', hour='0')
	# lambda passes function as parameter
	# cron is a configuration for time schedules
	# configured for everyday of week (0-6), at 12 AM (0)
clone_sched.start()


# homepage where user can select/add a repository to begin analysis process
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		repo_list = [ item for item in os.listdir(repo_dir) 
			if os.path.isdir(os.path.join(repo_dir, item)) ]
			# a list of all currently cloned repositories
			# refreshes everytime user chooses a new repository
		return render_template('index.html', 
			repo_list=repo_list, list_of_projects=list_of_projects)
	elif request.method == 'POST':
		if request.form['submit_button'] == "2":
			# if a selection was made from 'Available Repositories'
			repo_name = request.form['repo_name']
			from_date = request.form['from_date']
			to_date = request.form['to_date']
			root_dir = generator.select_folder(
				repo_dir, repo_name, from_date, to_date
			)	# select_folder called to handle folders and files
				# returns address of folder that contains csv files
			return redirect(url_for(
				'dashboard',
				root_dir=root_dir, repo_name=repo_name, 
				from_date=from_date, to_date=to_date
			)) 	# redirects to dashboard view which opens input.html
		elif request.form['submit_button'] == "1":
			# if user provided a clone url and password
			clone_url = request.form['clone_url']
			password = request.form['password']
			message = generator.submit_url(clone_url, password)
				# submit_url called to handle cloning of repo
			flash(message) # displays a confirmation message on the screen
			return redirect(url_for('index'))
		elif request.form['submit_button'] == "3":
			# if a selection was made from 'Stash Repositories'
			project_name = request.form['project_name']
			# project_desc = stash_api.get_details() # needs to be modified for this
			return redirect(url_for('index_repo', project_name=project_name))
			# project_description=generator.project_description))


# page where user can select a repository after selecting a Stash project
@app.route('/index_repo', methods=['GET', 'POST'])
def index_repo():
	# retrieves passed in query from index view
	project_name = request.args.get('project_name') 
	project_repos = stash_api.get_project_repos(project_name) 
		# dictionary of repos in Stash belong to selected project

	if request.method == 'GET':
		return render_template('index_repo.html', repo_list=project_repos)
	elif request.method == 'POST' and not request.form['repo_name'] == "":
		selected_repo = request.form['repo_name'].split('|')
		repo_name = selected_repo[0]
		repo_url = selected_repo[1] # string: clone url
		from_date = request.form['from_date']
		to_date = request.form['to_date']
		generator.submit_url(repo_url, settings.password) # uses our pass
		root_dir = generator.select_folder(
			repo_dir, repo_name, from_date, to_date
		)
		return redirect(url_for(
			'dashboard',
			root_dir=root_dir, repo_name=repo_name, 
			from_date=from_date, to_date=to_date
		))
			# after selecting a repo, the user is returned to the homepage 
			# where selected repo is now added to list of available repos
			# TO DO: skip the step of returning to homepage?


# page where user can select the specific analysis to view
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	# retrieves passed in queries from index view
	root_dir = request.args.get('root_dir')
	repo_name = request.args.get('repo_name')
	from_date = request.args.get('from_date')
	to_date = request.args.get('to_date')

	if request.method == 'GET':
		csv_list = []
		for root, dirs, files in os.walk(root_dir):
			# traverses filesystem of root_dir
			for filename in fnmatch.filter(files, '*.csv'):  
				# traverses files and picks out csv files
				csv_list.append(filename) # list of csv files
		return render_template('input.html', csv_list=csv_list) 
			# NOTE: csv_list currently not being used in webpage
			# TO DO: get rid of csv_list and have all csv's always available?
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
	if analysis == "cloud":
		with open("csv_files_" + repo_name + "_" + from_date + "_" + to_date + "/"
		+ analysis + "_" + repo_name + "__.log", 'rt') as log_file:
			word_list = generator.get_word_frequency(log_file)
		return render_template('wordcloud.html', 
		word_list=word_list, repo_name=json.dumps(repo_name), analysis=json.dumps(analysis),
		from_date=from_date, to_date=to_date)
	else:
		with open("csv_files_" + repo_name + "_" + from_date + "_" + to_date + "/"
			+ analysis + "_" + repo_name + ".csv", 'rt') as csv_file:
			# opens respective csv file for chosen analysis
			data, keys = generator.parse_csv(csv_file) 
				# calls parse_csv to retrieve data from csv file
			return render_template('result.html', 
				repo_name=json.dumps(repo_name), analysis=json.dumps(analysis),
				from_date=from_date, to_date=to_date, 
				data=json.dumps(data), keys=json.dumps(keys))
					# json.dumps() converts data into a string format for javascript


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
	app.run()
	# app.run(host='0.0.0.0')