from flask import Flask, request, render_template
import csv, os, time
from werkzeug import secure_filename

app = Flask(__name__)

# -------------------------------------------------------------------

# code below only works with code maat downloaded 
# and script is run from the repository directory

def create():
    print("Setting a path for codemaat...")
    # setting the path doesn't work 100% of the time when script is run
    os.system("PATH=/home/tramain/ixmaat0.8.5:$PATH")
    os.system("PATH=$PATH:/home/tramain/ixmaat0.8.5")
    print("Done.")
    print("-" * 60)
    print("Obtaining repository logs...")
    os.system("git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat > logfile.log")
    print("Done.")
    print("-" * 60)
    print("Creating csv file from generated log...")
    os.system("maat -l logfile.log -c git -a summary > summary.csv")
    print("Done. Check your current folder for your files.")
    print("-" * 60);

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
	# if request.method == 'GET':
	# 	return render_template('input.html')
	
	# when user selects a repo, the following runs codemaat and generates a csv file
	# the csv file is opened and parsed; visualization is displayed
	# elif request.method == 'POST':
	with open('summary.csv', 'rt') as csvfile:
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
    create()
    browser()
    app.run()
    #app.run(host='0.0.0.0')