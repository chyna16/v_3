import os
import fnmatch
import json
import generator
from flask import Flask, request, render_template, redirect, url_for

# owd = obtain working directory
owd = os.getcwd()
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	generator.clone_url = ""
	generator.password = ""
	generator.repo_name = ""
	if request.method == 'GET':
		folder_select = []
		for folder_name in generator.folder_list:
			folder_select.append(folder_name)  # fills array with names of csv files in current directory
		return render_template('index.html', folder_select=folder_select)  # returns array of csv filenames to webpage
	elif request.method == 'POST' and not request.form['clone_url'] == "":
			generator.clone_url = request.form['clone_url']
			generator.password = request.form['password']
			generator.submit_url()
			return redirect(url_for('index'))
	elif request.method == 'POST' and not request.form['folder_name'] == "": 
			select_folder()
			return redirect(url_for('dashboard'))

	
@app.route('/index_project', methods=['GET', 'POST'])
def index_project():
	generator.clone_url = ""
	generator.password = ""
	generator.repo_name = ""
	if request.method == 'GET':
		project_select = generator.project_list
		print(project_select)
		return render_template('index_project.html', project_select=project_select)  # returns array of csv filenames to webpage
	elif request.method == 'POST' and not request.form['clone_url'] == "":
			generator.clone_url = request.form['clone_url']
			generator.password = request.form['password']
			generator.submit_url()
			return redirect(url_for('index_project'))
	elif request.method == 'POST' and not request.form['folder_name'] == "": 
			select_folder()
			return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	global data
	global keys
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
		with open("csv_files_" + generator.repo_name + "_" 
			+ generator.date_after + "_" + generator.date_before 
			+ "/{}".format(csv_name), 'rt') as csv_file:
			data, keys = generator.parse_csv(csv_file)
		return redirect(url_for('result'))


@app.route('/result', methods=['GET', 'POST'])
def result():
	return render_template('result.html', repo_name=generator.repo_name,
	 data=json.dumps(data), keys=json.dumps(keys), 
	 date_after=generator.date_after, date_before=generator.date_before)


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


def select_folder():
	global root_dir
	print (request.form['folder_name'])
	generator.repo_name = request.form['folder_name']  # gets name of repository that was selected by the user on webpage
	# print (generator.repo_name)
	generator.set_path(generator.repo_name)
	generator.date_after = request.form['date_after']
	generator.date_before = request.form['date_before']
	# print (generator.date_after)
	# print (generator.date_before)
	root_dir = (owd + '/csv_files_' + generator.repo_name + "_" 
		+ generator.date_after + "_" + generator.date_before)
	# if directory already exists, skip function and go to the next page
	if(os.path.exists(generator.repo_list + "v3/csv_files_" 
		+ generator.repo_name + "_" + generator.date_after + "_" 
		+ generator.date_before)): 
		print("folder exists:" + generator.repo_list + "v3/csv_files_" 
			+ generator.repo_name + "_" + generator.date_after + "_" 
			+ generator.date_before)
		return redirect(url_for('dashboard'))
	else:
		generator.generate_data(address = generator.repo_list + generator.repo_name + '/.git')


if __name__ == '__main__':
	app.run(debug=True)
	# app.run(host='0.0.0.0')