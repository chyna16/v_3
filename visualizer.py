# 405 error fixed, route wasn't accepting any url methods
# fixed by adding 'methods = ['GET', 'POST']' to route parameters
# View function did not return a response error fixed
# fixed by replacing print with return on line 21
from flask import Flask, request, render_template
import csv

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def input():
    if request.method == 'GET':
        return render_template('input.html')
    elif request.method == 'POST':
        data = request.form['data']
    dataType = []
    dataValue = []
    with open(data, 'rt') as csvfile:
        # each row read from ths csv is returned as a list of strings
        fieldnames = ['item', 'value']
        readInfo = csv.DictReader(csvfile, fieldnames=fieldnames)
        # add a row
        for row in readInfo:
            dataType.append(row['item'])
            dataValue.append(row['value'])

    return render_template('result.html', dataType=dataType, dataValue=dataValue)

#  experimental

# 	else:
# 		return ('ERROR')

if __name__ == '__main__':
    app.debug = True
    app.run()
    #app.run(host='0.0.0.0')
