# 405 error fixed, route wasn't accepting any url methods
# fixed by adding 'methods = ['GET', 'POST']' to route parameters
# fixed View function did not return a response error
# fixed by replacing print with return on line 21
from flask import Flask, request, render_template
import csv
import os
from werkzeug import secure_filename

app = Flask(__name__)

# -------------------------------------------------------------------

# code below only works with code maat downloaded 
# and script is run from the repository directory

# def path():
#     print("Setting a path for codemaat...")
#     os.system("PATH=/home/tramain/ixmaat0.8.5:$PATH")
#     os.system("PATH=$PATH:/home/tramain/ixmaat0.8.5")
#     print("Done.");


# def read():
#     print("Obtaining repository logs...")
#     os.system("git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat > logfile.log")
#     print("Done.");

# def create():
#     print("Creating csv file from generated log...")
#     os.system("maat -l logfile.log -c git -a summary > summary.csv")
#     print("Done. Check your current folder for your files.");

# def browser():
# 	print("Process complete. Opening browser to http://127.0.0.1:5000/")
# 	os.system("google-chrome http://127.0.0.1:5000")

# --------------------------------------------------------------------

# this function takes csv file and two empty arrays
# reads each column from file into an array and returns the arrays
def parseCSV(uploadedFile, dataT, dataV):
	readInfo = csv.DictReader(uploadedFile)
	for row in readInfo:
		dataT.append(row['statistic'])
		dataV.append(int(row['value']))
	return dataT, dataV;

@app.route('/', methods=['GET', 'POST'])
def input():
	dataType = []
	dataValue = []

	# upon opening the homepage, user is prompted with a selection of repos
	if request.method == 'GET':
		return render_template('input.html')

	# when user selects a repo, the following runs codemaat and generates a csv file
	# the csv file is opened and parsed; visualization is displayed
	elif request.method == 'POST':
		# path()
		# read()
		# create()
		with open('summary.csv', 'rt') as csvfile:
			parseCSV(csvfile, dataType, dataValue)
		return render_template('result.html', dataType=dataType, dataValue=dataValue)


# THIS NEEDS TO BE WORKED ON
# TRYING TO GET ROUTE('/') TO REDIRECT TO BELOW ROUTE AFTER RENDER_TEMPLATE
# @app.route('/result', methods=['GET', 'POST'])
# def output():
# 	return render_template('result.html')


if __name__ == '__main__':
    app.debug = True
    app.run()


