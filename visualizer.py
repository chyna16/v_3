from flask import Flask, request, render_template
import csv, os, time, fnmatch
from werkzeug import secure_filename

rootPath = '/home/tramain/repos/v3/csv_files'
# rootPath = '/home/ubuntu/Desktop/repos/v3clone/v3/csv_folder'
pattern = '*.csv'

app = Flask(__name__)

# -------------------------------------------------------------------

# code below only works with code maat downloaded 
# and script is run from the repository directory

def set_path():
	print("Setting a path for codemaat...")
	# path is set temporarily, per script run
	os.environ['PATH'] += os.pathsep + '/home/tramain/ixmaat0.8.5'
	print("Done.")
	print("-" * 60)
	# need to create an exception if folder already exists
	# global owd
	# owd = os.getcwd()
	os.system("mkdir csv_files")
	os.chdir("csv_files")

def create():
	print("Obtaining repository logs...")
	os.system("git --git-dir /home/tramain/mcshake/.git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat > logfile.log")
	print("Done.")
	print("-" * 60)
	print("Creating csv files from generated log...")
	time.sleep(1)
	print("Creating repository summary...")
	os.system("maat -l logfile.log -c git -a summary > summary.csv")
	# Reports an overview of mined data from git's log file
	print("Creating organizational metrics summary...")
	os.system("maat -l logfile.log -c git > metrics.csv")
	# Reports the number of authors/revisions made per module
	print("Creating coupling summary...")
	os.system("maat -l logfile.log -c git -a coupling > coupling.csv")
	# Reports correlation of files that often commit together
	# degree = % of commits where the two files were changed in the same commit
	print("Creating code age summary...")
	os.system("maat -l logfile.log -c git -a entity-churn > age.csv")
	# Reports how long ago the last change was made in measurement of months
	print("Done. Check your current folder for your files.")
	print("-" * 60)
	# os.chdir(owd);

def browser():
	print("Process complete. Opening browser to http://127.0.0.1:5000/")
	time.sleep(2)
	os.system("google-chrome-stable http://127.0.0.1:5000")
	print("-" * 60);

# --------------------------------------------------------------------

# this function takes csv file and two empty arrays
# reads each column from file into an array and returns the arrays
def parseCSV(uploadedFile, dataT, dataV):
	readInfo = csv.DictReader(uploadedFile)
	for row in readInfo:
		dataT.append(row['statistic'])
		dataV.append(row['value'])
	return dataT, dataV;

@app.route('/', methods=['GET', 'POST'])
def input():
	dataType, dataValue = [], []
	
	# upon opening the homepage, user is prompted with a selection of repos
	if request.method == 'GET':
		csvList = []
		for root, dirs, files in os.walk(rootPath): # traverses filesystem of rootPath
			for filename in fnmatch.filter(files, pattern): # picks out files of type in pattern
				csvList.append(filename) # fills array with names of csv files in current directory
		return render_template('input.html', csvList=csvList) # returns array of csv filenames to webpage
	
	# when user selects a repo, the following runs codemaat and generates a csv file
	# the csv file is opened and parsed; visualization is displayed
	elif request.method == 'POST':
		data = request.form['filename'] # gets name of csv filename that was selected by the user on webpage
		with open('{}'.format(data), 'rt') as csvfile: # variable data SHOULD be in form of 'csvname.csv'
			parseCSV(csvfile, dataType, dataValue)
		return render_template('result.html', dataType=dataType, dataValue=dataValue)
		csvfile.close();

# THIS NEEDS TO BE WORKED ON
# TRYING TO GET ROUTE('/') TO REDIRECT TO BELOW ROUTE AFTER RENDER_TEMPLATE
# @app.route('/result', methods=['GET', 'POST'])
# def output():
# 	return render_template('result.html')

if __name__ == '__main__':
	# debug mode causes create() function to run twice
	# app.debug = True
	set_path()
	create()
	browser()
	app.run()
	#app.run(host='0.0.0.0')