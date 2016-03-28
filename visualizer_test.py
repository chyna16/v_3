import csv, os, time, fnmatch, json
# from flask.ext.bootstrap import Bootstrap
from flask import Flask, request, render_template, redirect, url_for

# this is the directory of where the html page obtains the list of files to select from
# owd = obtain working directory
owd = os.getcwd()

# currently the codemaat directory is hardcoded

if os.name == 'nt':
	# root_dir = os.path.normpath(owd + '/csv_files_' + repo_name)
	maat_dir = os.path.normpath('C:/Users/bentinct/winmaat0.8.5/')
	repo_dir = os.path.normpath('C:/Users/bentinct/repos/mcshake/.git')
	repo_list = ('C:\\Users\\bentinct\\repos\\')
	# repo_name = os.path.basename(os.path.normpath(repo_dir))
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]
else:
	# root_dir = owd + '/csv_files_' + repo_name
	maat_dir = '/home/tramain/ixmaat0.8.5'
	repo_dir = '/home/tramain/mcshake/.git'

# this returns only files of this type to the html page to display.
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
def parse_csv(uploaded_file, data_array):
	row_array = []
	length = 0
	i = 0
	reader = csv.reader(uploaded_file)
	for row in reader:
		length = len(row)
		row_array.append(row)
	print(row_array[0])
	while i < length:
		col_array = []
		for r in row_array:
			col_array.append(r[i])
		data_array.append(col_array)
		i += 1
	return data_array


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
		generate_data(address = repo_list + repo_name + '\.git')
		# os.chdir(repo_list + repo_name + '/.git')
	# 	with open("{}".format(data), 'rt') as test_file:  # variable data SHOULD be in form of 'csvname.csv'
	# 		parse_csv(csv_file, data_array)
		print (os.getcwd())
		return redirect(url_for('dashboard'))
	
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	global data_array
	data_array = []

	# upon opening the homepage, user is prompted with a selection of repos
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
		data = request.form['filename']  # gets name of csv filename that was selected by the user on webpage
		with open("csv_files_" + repo_name + "/{}".format(data), 'rt') as csv_file:  # variable data SHOULD be in form of 'csvname.csv'
			parse_csv(csv_file, data_array)
		csv_file.close()
		return redirect(url_for('result'))

@app.route('/result', methods=['GET', 'POST'])
def result():
	return render_template('result.html', 
			data_array=json.dumps(data_array), repo_name=repo_name)


@app.errorhandler(404)
def not_found(e):
	return render_template ('404.html')

@app.errorhandler(400)
def bad_request(e):
	return render_template ('400.html')

if __name__ == '__main__':
	# debug mode causes generate_data() function to run twice
	app.debug = True
	# set_path()
	# generate_data()
	# open_browser()
	
	app.run()
	# app.run(host='0.0.0.0')
