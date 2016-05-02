import os
import fnmatch
import json
import generator
# import stash_api
from flask import Flask, request, render_template, redirect, url_for, flash, session

# owd = obtain working directory
owd = os.getcwd()
app = Flask(__name__)
secret = os.urandom(24)
app.secret_key = secret


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	# clone_url = ""
	# password = ""
	# repo_name = ""
	if request.method == 'GET':
		folder_select = []
		for folder_name in generator.folder_list:
			folder_select.append(folder_name)  # fills array with names of csv files in current directory
		return render_template('index.html', folder_select=folder_select)  # returns array of csv filenames to webpage
	elif request.method == 'POST':
		if not request.form['clone_url'] == "" and request.form['folder_name'] == "":
			clone_url = request.form['clone_url']
			password = request.form['password']
			generator.submit_url(clone_url, password)
			flash('Cloning Complete.')
			return redirect(url_for('index'))
		elif not request.form['folder_name'] == "" and request.form['clone_url'] == "":
			selected_repo = request.form['folder_name']
			if selected_repo == "projects":
				print("Going to index_project")
				return redirect(url_for('index_project'))
			else:
				root_dir, date_after, date_before = select_folder(selected_repo)
				return redirect(url_for('dashboard', 
					selected_repo=selected_repo, date_after=date_after, date_before=date_before, root_dir=root_dir))

	
@app.route('/index_project', methods=['GET', 'POST'])
def index_project():
	# generator.clone_url = ""
	# generator.password = ""
	# generator.repo_name = ""
	list_of_projects = generator.project_keys
	if request.method == 'GET':
		return render_template('index_project.html', project_select=list_of_projects)  # returns array of csv filenames to webpage
	# elif request.method == 'POST' and not request.form['clone_url'] == "":
	# 		generator.clone_url = request.form['clone_url']
	# 		generator.password = request.form['password']
	# 		generator.submit_url()
	# 		flash('Cloning complete.')
	# 		return redirect(url_for('index_project'))
	elif request.method == 'POST' and not request.form['project_name'] == "":
		selected_project = request.form['project_name']

		print(request.form['project_name'])
		# for project in list_of_projects:
			# if request.form['project_name'] == project:
		project_repo_names, project_repo_urls = generator.get_project_key(selected_project)
		return redirect(url_for('index_repo', names=project_repo_names, links=project_repo_urls))
			# select_folder()
			# print(request.form['project_name'])
			# return redirect(url_for('dashboard'))


@app.route('/index_repo', methods=['GET', 'POST'])
def index_repo():
	# generator.clone_url = ""
	# generator.password = ""
	# generator.repo_name = ""
	if request.method == 'GET':
		return render_template('index_repo.html', 
		repo_select=request.args.get('names'), repo_url=request.args.get('links'))  # returns array of csv filenames to webpage

	# elif request.method == 'POST' and not request.form['clone_url'] == "":
	# 		generator.clone_url = request.form['clone_url']
	# 		generator.password = request.form['password']
	# 		generator.submit_url()
	# 		flash('Cloning Complete.')
	# 		return redirect(url_for('index'))
	elif request.method == 'POST' and not request.form['repo_name'] == "":
			# temporary redirect
			selected_repo = request.form['repo_name']
			# generator.clone_url = selected_repo
			generator.submit_url(selected_repo, 'viacom4040')
			return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	root_dir = request.args.get('root_dir')
	date_after = request.args.get('date_after')
	date_before = request.args.get('date_before')
	repo_name = request.args.get('selected_repo')
	if request.method == 'GET':
		csv_list = []
		# this is the directory of where the html page obtains the list of files to select from
		for root, dirs, files in os.walk(root_dir):  # traverses filesystem of root_dir
			for filename in fnmatch.filter(files, generator.file_type):  # picks out files of type in pattern
				csv_list.append(filename)  # fills array with names of csv files in current directory
		return render_template('input.html', csv_list=csv_list)  # returns array of csv filenames to webpage
	# when user selects a repo, the following runs codemaat and generates a csv file
	# the csv file is opened and parsed; visualization is displayed
	elif request.method == 'POST':
		csv_name = request.form['filename']  # gets name of csv filename that was selected by the user on webpage
		return redirect(url_for('result', csv_name=csv_name, repo_name=repo_name, 
			date_after=date_after, date_before=date_before))


@app.route('/result', methods=['GET', 'POST'])
def result():
	with open("csv_files_" 
			+ request.args.get('repo_name') + "_" 
			+ request.args.get('date_after') + "_" + request.args.get('date_before') + "/" 
			+ request.args.get('csv_name'), 'rt') as csv_file:
		data, keys = generator.parse_csv(csv_file)
	return render_template('result.html', repo_name=request.args.get('repo_name'), 
		data=json.dumps(data), keys=json.dumps(keys), 
		date_after=request.args.get('date_after'), date_before=request.args.get('date_before'))


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


def select_folder(repo):
	# global root_dir
	print (request.form['folder_name'])
	# generator.repo_name = repo  # gets name of repository that was selected by the user on webpage
	# print (generator.repo_name)
	generator.set_path(repo)
	date_after = request.form['date_after']
	date_before = request.form['date_before']
	# print (generator.date_after)
	# print (generator.date_before)
	root_dir = (owd + '/csv_files_' + repo + "_" 
		+ date_after + "_" + date_before)
	# if directory already exists, skip function and go to the next page
	if(os.path.exists(generator.repo_list + "v3/csv_files_" 
		+ repo + "_" + date_after + "_" 
		+ date_before)): 
		print("folder exists:" + generator.repo_list + "v3/csv_files_" 
			+ repo + "_" + date_after + "_" 
			+ date_before)
		flash('Directory exists, redirected to current page.')
		# return redirect(url_for('dashboard'))
	else:
		generator.generate_data(repo, date_after, date_before, generator.repo_list + repo + '/.git')
		flash('Analysis complete.')

	return (root_dir, date_after, date_before)

# def select_repo():
# 	# global root_dir
# 	print (request.form['folder_name'])
# 	generator.repo_name = request.form['folder_name']  # gets name of repository that was selected by the user on webpage
# 	# print (generator.repo_name)
# 	generator.set_path(generator.repo_name)
# 	generator.date_after = request.form['date_after']
# 	generator.date_before = request.form['date_before']
# 	# print (generator.date_after)
# 	# print (generator.date_before)
# 	root_dir = (owd + '/csv_files_' + generator.repo_name + "_" 
# 		+ generator.date_after + "_" + generator.date_before)
# 	# if directory already exists, skip function and go to the next page
# 	if(os.path.exists(generator.repo_list + "v3/csv_files_" 
# 		+ generator.repo_name + "_" + generator.date_after + "_" 
# 		+ generator.date_before)): 
# 		print("folder exists:" + generator.repo_list + "v3/csv_files_" 
# 			+ generator.repo_name + "_" + generator.date_after + "_" 
# 			+ generator.date_before)
# 		flash('Directory exists, redirected to current page.')
# 		return redirect(url_for('dashboard'))
# 	else:
# 		generator.generate_data(address = generator.repo_list + generator.repo_name + '/.git')
# 		flash('Analysis complete.')

if __name__ == '__main__':
	app.run(debug=True)
	# app.run(host='0.0.0.0')