import csv, os, time, fnmatch, json
# from flask.ext.bootstrap import Bootstrap
from flask import Flask, request, render_template, redirect, url_for

# this is the directory of where the html page obtains the list of files to select from
# owd = obtain working directory
owd = os.getcwd()

# currently the codemaat directory is hardcoded

if os.name == 'nt':
	# root_dir = os.path.normpath(owd + '/csv_files_' + repo_name)
	maat_dir = ('C:\\Users\\bentinct\\winmaat0.8.5\\')
	repo_dir = ('C:\\Users\\bentinct\\repos\\mcshake\\.git')
	repo_list = ('C:\\Users\\bentinct\\repos\\')
	# repo_name = os.path.basename(os.path.normpath(repo_dir))
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]
else:
	# root_dir = owd + '/csv_files_' + repo_name
	maat_dir = '/home/tramain/ixmaat0.8.5'
	# maat_dir = '/home/farhat/ixmaat0.8.5'
	repo_dir = '/home/tramain/mcshake/.git'
	# repo_dir = '/home/farhat/Desktop/repos/mcshake/.git'
	repo_list = '/home/tramain/repos/'
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]

# this returns only files of this type to the dashboard function to display.
file_type = '*.csv'

app = Flask(__name__)

# bootstrap = Bootstrap(app)
# code below only works with codemaat downloaded
def set_path(repo_name):
	print("Setting a path for codemaat...")
	# path is set temporarily, per script run
	os.environ['PATH'] += os.pathsep + maat_dir
	print("Done.")
	print("-" * 60)
	# need to create an exception if csv_files folder already exists
	# global owd
	# owd = os.getcwd()
	# creates folder for the root_dir variable if none exists
	os.system("mkdir csv_files_" + repo_name)
	os.chdir("csv_files_" + repo_name)


def generate_data(address):
	print("Obtaining repository logs...")
	# currently manually selects the repository
	os.system('git --git-dir ' + address + ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat > logfile_' + repo_name + '.log')
	print("Done.")
	print("-" * 60)
	print("Creating csv files from generated log...")
	time.sleep(1)
	print("Creating repository summary...")
	# currently running codemaat via 'maat.bat' on windows creates extra lines of code in the csv files,
	# causing them to break when requested from the site
	os.system("maat -l logfile_" + repo_name + ".log -c git -a summary > summary_" + repo_name + ".csv")
	# Reports an overview of mined data from git's log file
	print("Creating organizational metrics summary...")
	os.system("maat -l logfile_" + repo_name + ".log -c git > metrics_" + repo_name + ".csv")
	# Reports the number of authors/revisions made per module
	print("Creating coupling summary...")
	os.system("maat -l logfile_" + repo_name + ".log -c git -a coupling > coupling_" + repo_name + ".csv")
	# Reports correlation of files that often commit together
	# degree = % of commits where the two files were changed in the same commit
	print("Creating code age summary...")
	os.system("maat -l logfile_" + repo_name + ".log -c git -a entity-churn > age_" + repo_name + ".csv")
	# Reports how long ago the last change was made in measurement of months
	print("Done. Check your current folder for your files.")
	print("-" * 60)
	os.chdir("..")


def open_browser():
	print("Process complete. Opening browser to http://127.0.0.1:5000/")
	time.sleep(2)
	os.system("google-chrome-stable http://127.0.0.1:5000")
	print("-" * 60)


# this function takes csv file and two empty arrays
# reads each column from file into an array and returns the arrays
def parse_csv(uploaded_file):
	reader = csv.reader(uploaded_file)
	data_dict = {}
	key_array = []
	row_array = []

	for i, row in enumerate(reader):
		if i == 0:
			key_array = row
		else:
			row_array.append(row)

	for i, key in enumerate(key_array):
		col_array = []
		for r in row_array:
			col_array.append(r[i])
		data_dict[key] = col_array

	return (data_dict, key_array)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		folder_select = []
		for folder_name in folder_list:
			folder_select.append(folder_name)  # fills array with names of csv files in current directory
		return render_template('index.html', folder_select=folder_select)  # returns array of csv filenames to webpage
	elif request.method == 'POST':
		# print(repo_list + '\\' + folder_name)
		global repo_name
		repo_name = request.form['folder_name']  # gets name of csv filename that was selected by the user on webpage
		print (repo_name)
		set_path(repo_name)
		if os.name == 'nt':
			generate_data(address = repo_list + repo_name + '\.git')
		else:
			generate_data(address = repo_list + repo_name + '/.git')
		# os.chdir(repo_list + repo_name + '/.git')
		return redirect(url_for('dashboard'))
	

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	global data
	global keys

	if request.method == 'GET':
		csv_list = []
		if os.name == 'nt':
			root_dir = os.path.normpath(owd + '/csv_files_' + repo_name)
		else:
			root_dir = owd + '/csv_files_' + repo_name
		for root, dirs, files in os.walk(root_dir):  # traverses filesystem of root_dir
			for filename in fnmatch.filter(files, file_type):  # picks out files of type in pattern
				csv_list.append(filename)  # fills array with names of csv files in current directory
		return render_template('input.html', csv_list=csv_list)  # returns array of csv filenames to webpage

	# when user selects a repo, the following runs codemaat and generates a csv file
	# the csv file is opened and parsed; visualization is displayed
	elif request.method == 'POST':
		csv_name = request.form['filename']  # gets name of csv filename that was selected by the user on webpage
		with open("csv_files_" + repo_name + "/{}".format(csv_name), 'rt') as csv_file:
			data, keys = parse_csv(csv_file)
		csv_file.close()
		return redirect(url_for('result'))


@app.route('/result', methods=['GET', 'POST'])
def result():
	return render_template('result.html', data=json.dumps(data), keys=json.dumps(keys))


# this filter allows using '|fromjson', which calls this json.loads function
@app.template_filter('fromjson')
def convert_json(s):
	return json.loads(s)

@app.errorhandler(404)
def not_found(e):
	return render_template ('404.html')

@app.errorhandler(400)
def bad_request(e):
	return render_template ('400.html')

if __name__ == '__main__':
	# debug mode causes generate_data() function to run twice
	app.debug = True
	# open_browser()
	
	app.run()
	# app.run(host='0.0.0.0')
