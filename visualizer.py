# 405 error fixed, route wasn't accepting any url methods
# fixed by adding 'methods = ['GET', 'POST']' to route parameters
# fixed View function did not return a response error
# fixed by replacing print with return on line 21
from flask import Flask, request, render_template
import csv
import os
from werkzeug import secure_filename

app = Flask(__name__)
# code below only works with code maat downloaded and script is run from the
# repository directory

def path():
    print("Setting a path for codemaat...")
    os.system("PATH=/home/tramain/ixmaat0.8.5:$PATH")
    os.system("PATH=$PATH:/home/tramain/ixmaat0.8.5")
    print("Done.");


def read():
    print("Obtaining repository logs...")
    os.system("git log --pretty=format:'[%h] %aN %ad %s' --date=short --numstat > logfile.log")
    print("Done.");

def create():
    print("Creating csv file from generated log...")
    os.system("maat -l logfile.log -c git -a summary > summary.csv")
    print("Done. Check your current folder for your files.");

def browser():
	print("Process complete. Opening browser to http://127.0.0.1:5000/")
	os.system("google-chrome http://127.0.0.1:5000")


path()
read()
create()
browser()

@app.route('/', methods=['GET', 'POST'])
def input():
    # set an empty list for our csv to fill
    # data = request.files['summary.csv']
    # filename = secure_filename(data.filename)
    # data.save(filename)
    dataType = []
    dataValue = []
    # open csv file
    with open('summary.csv', 'rt') as csvfile:
        # fieldnames = ['item']
        # each row read from ths csv is returned as a list of strings
        # fieldnames = ['Month', 'commits']
        readInfo = csv.DictReader(csvfile)
        # add a row
        for row in readInfo:
            dataType.append(row['statistic'])
            dataValue.append(row['value'])

    return render_template('result.html', dataType=dataType, dataValue=dataValue);
    # csvfile.close()


# else:
# 	return ('ERROR')
#  experimental

if __name__ == '__main__':
    app.debug = True
    app.run()
    #app.run(host='0.0.0.0')


