import csv
import os
import fnmatch
import glob
import subprocess
from flask import request, flash
from stop_words import get_stop_words
import stash_api
import settings
import data_manager
import repo_manager
import shutil
from nltk.stem.lancaster import LancasterStemmer
from datetime import datetime


# called by index view to set path for codemaat
# sets the path to the passed in address
def set_path(path):
	print("Setting a path to " + path)
	os.environ['PATH'] += os.pathsep + path
	print("Done.")
	print("-" * 60)


# returns a bool after checking date is in correct yyyy-mm-dd form
def valid_date(date):
	date = date.split(' ')[0].split('-')
	if not len(date) == 3:
		return False
	try:
		correct_date = datetime(int(date[0]), int(date[1]), int(date[2]))
		return True
	except ValueError:
		return False

# called by index view
def bad_range(start,end):
	if not valid_date(start) and not valid_date(end):
		return True
	elif start > end:
		return True
	return False

# called by generate_data functions
# helper function to handle command line input for running codemaat
def run_codemaat(analysis_type, analysis_name, repo_name, from_date, to_date):
	os.system("maat -l logfile_"
		+ repo_name + "_" + from_date + "_" + to_date
		+ ".log -c git -a " + analysis_type + " > "
		+ analysis_name + "_" + repo_name + ".csv")


# runs cloc to retrieve number of lines of code
# merges with metrics data to show hotspots
def generate_data_hotspots(repo_name, from_date, to_date, repo_dir=settings.repo_dir):
	print("Creating repository hotspots...")
	if not os.path.isfile("metrics_" + repo_name + ".csv"):
		print("Creating metrics...")
		run_codemaat('authors', 'metrics', repo_name, from_date, to_date)
	os.system("cloc " + os.path.join(repo_dir, repo_name)
		+ " --unix --by-file --csv --quiet --report-file="
		+ "lines_" + repo_name + ".csv")
	data_manager.merge_csv(repo_name)
	print("-" * 60)


# called by: process_log
# handles command line inputs for creating a logfile / wordlog
def create_log(log_type, repo_name, from_date, to_date, address):
	print("Obtaining repository logs...")
	sys_command = 'git --git-dir ' + address + ' log --pretty=format:'
	if log_type == 'cloud': sys_command += '"%s"'
	else: sys_command += '"[%h] %aN %ad %s" --date=short --numstat'
	if from_date: sys_command += ' --after=' + from_date
	if to_date: sys_command += ' --before=' + to_date
	sys_command += (' > '
		+ log_type +'_'+ repo_name +'_'+ from_date +'_'+ to_date + '.log')
	os.system(sys_command)
	print("Done.")
	print("-" * 60)


#obtains complexity history of repository
#can take a long time (up to 3 min)when running on large repositories
#requires the 'csvcat' python package
def create_complexity_files(repo, address, from_date, to_date):
	folder_name = repo + "_" + from_date + "_" + to_date
	#files to be ignored
	extensions = ('.png', '.csv', '.jpg', '.svg', '.html', '.less', '.swf',
	 '.spec', '.md', '.ignore', '.ttf', '.min', '.css', '.xml', '.pdf','.dmd',
	 '.properties', '.local', '.ftl')

	file_list = []
	csv_list = []
	git_list = []

	# get the log id of first and latest commit in the repository based on date
	first_id = subprocess.getoutput('git --git-dir ' + address
		+ ' log --pretty=format:"%h" --no-patch --reverse --after='
		+ from_date + ' --before=' + to_date + ' | head -1')
	last_id = subprocess.getoutput('git --git-dir ' + address
		+ ' log --pretty=format:"%h" --no-patch --after='
		+ from_date + ' --before=' + to_date + ' | head -1')
	# gets the list of commit IDs and their dates in ISO format
	git_values = subprocess.getoutput('git --git-dir ' + address
		+ ' log --pretty=format:"%h %ad" --date=iso --no-patch '
		+ '--reverse --after=' + from_date + ' --before=' + to_date)

	for item in git_values.splitlines():
		git_list.append(item)


	for root, dirs, files in os.walk(settings.repo_dir + repo):
		if '.git' in dirs:
			dirs.remove('.git')
		for file in files:
			if file.endswith(extensions):
				continue
			file_list.append(os.path.join(root, file))

	#runs complexity analysis script on each file in the repository
	for file in file_list:
		split_path = file.split(repo + '/')
		p = subprocess.Popen('python2 ' + settings.v3_dir
			+ '/git_complexity_trend.py --start ' + first_id
			+ ' --end ' + last_id + ' --file ' + split_path[1] + ' > '
			+ settings.csv_dir  + folder_name + '/complex_'
			+ os.path.basename(os.path.normpath(split_path[1])) + '.csv',
			cwd = os.path.join(settings.repo_dir, repo), shell=True)
		p.wait()

	os.chdir(os.path.join(settings.csv_dir, folder_name))

	for file in glob.glob("*.csv"):
		csv_list.append(file)

	#appends csv files together into one
	os.system(settings.csvcat_path + ' --skip-headers '
		+ (' '.join(csv_list)) + ' > ' + 'complex_' + repo + '.csv')

	#adds date column to csv file
	with open('complex_' + repo + '.csv','r') as csvinput:
		with open('complexity_' + repo + '.csv', 'w') as csvoutput:
			csv_write = csv.writer(csvoutput, lineterminator='\n')
			csv_reader = csv.reader(csvinput)

			all = []
			try:
				row = next(csv_reader)
				row.append('date')
				all.append(row)

				for row in csv_reader:
					for item in git_list:
						if item.split(' ')[0] in row:
							row.append(item[10:])
							all.append(row)
				csv_write.writerows(all)
			except:
				print('No Complexity')
	for file in glob.glob("complex_*"):
		os.remove(file)

	os.chdir(settings.v3_dir)

# called by: manage_csv_folder, refresh_repos
# generates log file and runs codemaat
def process_log(repo, from_date, to_date, csv_path):
	if not os.path.isdir(csv_path): os.system("mkdir " + csv_path)
		# if the csv_folder doesn't exist, make it
	os.chdir(csv_path)
	# cd into the folder and create logs and csv files
	repo_address = os.path.join(settings.repo_dir, repo, '.git')
	create_log('logfile', repo, from_date, to_date, repo_address)
	create_log('cloud', repo, from_date, to_date, repo_address)
	create_complexity_files(repo, repo_address, from_date, to_date)
	os.chdir(csv_path)
	print("Running codemaat analyses")
	run_codemaat('authors', 'metrics', repo, from_date, to_date)
	run_codemaat('coupling', 'coupling', repo, from_date, to_date)
	run_codemaat('entity-churn', 'age', repo, from_date, to_date)
	generate_data_hotspots(repo, from_date, to_date)

	os.chdir(settings.v3_dir)


# called by: index view
# sets the address where csv files are/will be located
# calls helper functions that handle folder, logfile, & codemaat
def manage_csv_folder(repo, from_date, to_date, csv_dir=settings.csv_dir):
	folder_name = repo + "_" + from_date + "_" + to_date
	csv_path = os.path.join(csv_dir, folder_name)
		# complete address of csv folder for chosen repo
	if not os.path.exists(csv_path):
		print("creating folder: " + csv_path)
		os.system("mkdir " + csv_path)
		process_log(repo, from_date, to_date, csv_path)

		if os.stat(os.path.join(csv_path,
			"logfile_" + repo + '_' + from_date + '_' + to_date + '.log')
		).st_size == 0:
			# if the generated logfile does not have data
			return False
	else:
		print("folder exists: " + csv_path)
	return True

def analysis_exists(repo, from_date, to_date, csv_dir=settings.csv_dir):
	folder_name = repo + "_" + from_date + "_" + to_date
	csv_path = os.path.join(csv_dir, folder_name)

	if os.path.exists(csv_path):
		return True
	return False

# retrieved from: http://stackoverflow.com/questions/3424899/
# 	+ whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
# def monthdelta(date, delta):
# 	m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
# 	if not m: m = 12
# 	d = min(date.day, [31, 29 if
#		y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
# 	return date.replace(day=d,month=m, year=y)

# def get_prev_date():
# 	for m in range(-2, -1):
# 		month_string = str(monthdelta(datetime.now(), m))
# 	previous_date = ((month_string)[:10])

# 	return previous_date

# if __name__ == '__main__':
