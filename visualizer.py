<<<<<<< HEAD
import os, fnmatch, json, generator
=======
import os
import fnmatch
import json
import generator
>>>>>>> 38248f29103abd1bf3bc43f7dd9d30b7734abc68
from flask import Flask, request, render_template, redirect, url_for

# owd = obtain working directory
owd = os.getcwd()
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	global root_dir
	if request.method == 'GET':
		folder_select = []
		for folder_name in generator.folder_list:
			folder_select.append(folder_name)  # fills array with names of csv files in current directory
		return render_template('index.html', folder_select=folder_select)  # returns array of csv filenames to webpage
	elif request.method == 'POST':
		print (request.form['folder_name'])
		generator.repo_name = request.form['folder_name']  # gets name of repository that was selected by the user on webpage
		print (generator.repo_name)
		generator.set_path(generator.repo_name)
		generator.date_after = request.form['date']
		print (generator.date_after)
		root_dir = owd + '/csv_files_' + generator.repo_name
		# if directory already exists, skip function and go to the next page
		if(os.path.exists(generator.repo_list + "v3/csv_files_" + generator.repo_name)): 
			print("folder exists:" + generator.repo_list + "v3/csv_files_" + generator.repo_name)
			return redirect(url_for('dashboard'))
		else:
			generator.generate_data(address = generator.repo_list + generator.repo_name + '/.git')
		return redirect(url_for('dashboard'))
	

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	global data
	global keys
	global root_dir
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
		with open("csv_files_" + generator.repo_name + "/{}".format(csv_name), 'rt') as csv_file:
			data, keys = generator.parse_csv(csv_file)
		return redirect(url_for('result'))


@app.route('/result', methods=['GET', 'POST'])
def result():
	return render_template('result.html', repo_name=generator.repo_name, data=json.dumps(data), keys=json.dumps(keys))


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

if __name__ == '__main__':
	app.run(debug=True)
	# app.run(host='0.0.0.0')