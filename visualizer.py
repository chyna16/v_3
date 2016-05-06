import os
import fnmatch
import json
import generator
import stash_api
import settings
from flask import Flask, request, render_template, redirect, url_for, flash, session

# owd = obtain working directory
owd = os.getcwd()
app = Flask(__name__)
secret = os.urandom(24)
app.secret_key = secret

maat_dir = settings.maat_directory
repo_dir = settings.repo_directory


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		repo_list = [ item for item in os.listdir(repo_dir) if os.path.isdir(os.path.join(repo_dir, item)) ]
		return render_template('index.html', repo_list=repo_list)  # returns array of csv filenames to webpage
	elif request.method == 'POST':
		session['clone_url'] = request.form['clone_url']
		session['password'] = request.form['password']
		session['repo_name'] = request.form['repo_name']
		session['from_date'] = request.form['from_date']
		session['to_date'] = request.form['to_date']

		clone_url = session['clone_url']
		password = session['password']
		repo_name = session['repo_name']
		from_date = session['from_date']
		to_date = session['to_date']

		print(from_date)
		print(to_date)

		if not session['clone_url'] == "" and session['repo_name'] == "":
			generator.submit_url(clone_url, password)
			flash('Cloning Complete.')
			return redirect(url_for('index'))
		elif not session['repo_name'] == "":
			if session['repo_name'] == "projects":
				print("Going to index_project")
				return redirect(url_for('index_project'))
			else:
				session['root_dir'] = select_folder(repo_name, from_date, to_date)
				return redirect(url_for('dashboard'))

	
@app.route('/index_project', methods=['GET', 'POST'])
def index_project():
	list_of_projects = stash_api.get_projects()

	if request.method == 'GET':
		return render_template('index_project.html', list_of_projects=list_of_projects)  
	elif request.method == 'POST' and not request.form['project_name'] == "":
		session['project_name'] = request.form['project_name']
		return redirect(url_for('index_repo'))


@app.route('/index_repo', methods=['GET', 'POST'])
def index_repo():
	project_repos = stash_api.get_project_repos(session['project_name'])

	if request.method == 'GET':
		return render_template('index_repo.html', repo_list=project_repos)
	elif request.method == 'POST' and not request.form['repo_name'] == "":
		selected_repo = request.form['repo_name']
		generator.submit_url(selected_repo, settings.password)
		return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	root_dir = session['root_dir']
	repo_name = session['repo_name']
	from_date = session['from_date']
	to_date = session['to_date']

	if request.method == 'GET':
		csv_list = []
		# this is the directory of where the html page obtains the list of files to select from
		for root, dirs, files in os.walk(root_dir):  # traverses filesystem of root_dir
			for filename in fnmatch.filter(files, '*.csv'):  # picks out files of type in pattern
				csv_list.append(filename)  # fills array with names of csv files in current directory
		return render_template('input.html', csv_list=csv_list)  # returns array of csv filenames to webpage
	# when user selects a repo, the following runs codemaat and generates a csv file
	# the csv file is opened and parsed; visualization is displayed
	elif request.method == 'POST':
		session['csv_name'] = request.form['filename']  # gets name of csv filename that was selected by the user on webpage
		return redirect(url_for('result'))


@app.route('/result', methods=['GET', 'POST'])
def result():
	csv_name = session['csv_name']
	repo_name = session['repo_name']
	from_date = session['from_date']
	to_date = session['to_date']

	with open("csv_files_" 
			+ repo_name + "_" 
			+ from_date + "_" + to_date + "/"
			+ csv_name, 'rt') as csv_file:
		data, keys = generator.parse_csv(csv_file)
	return render_template('result.html', 
		repo_name=repo_name, csv_name=csv_name,
		from_date=from_date, to_date=to_date, 
		data=json.dumps(data), 
		keys=json.dumps(keys))


# this filter allows using '|fromjson', which calls this json.loads function
@app.template_filter('fromjson')
def convert_json(s):
	return json.loads(s)

# customized error pages that follow the style of the website
@app.errorhandler(404)
def not_found(e):
	return render_template ('404.html')


@app.errorhandler(400)
def bad_request(e):
	return render_template ('400.html')


def select_folder(repo, from_date, to_date):
	generator.set_path(maat_dir)
	root_dir = (owd + '/csv_files_' 
		+ repo + "_" 
		+ from_date + "_" + to_date)
	# if directory already exists, skip function and go to the next page
	if(os.path.exists(repo_dir + root_dir)):
		# + "v3/csv_files_" 
		# + repo + "_" + date_after + "_" 
		# + date_before)): 
		print("folder exists:" + repo_dir + root_dir)
		flash('Directory exists, redirected to current page.')
	else:
		generator.generate_data(repo_dir + repo + '/.git', 
			repo, from_date, to_date)
		flash('Analysis complete.')

	return (root_dir)



if __name__ == '__main__':
	app.run(debug=True)
	# app.run(host='0.0.0.0')