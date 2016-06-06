import csv
import os
import time
import fnmatch
import subprocess
from flask import request, flash
from stop_words import get_stop_words
import stash_api
import shutil


# called by visualizer at timed intervals
# updates already cloned repositories
def clone_repos(repo_dir, password):
	repo_list = [ item for item in os.listdir(repo_dir) 
			if os.path.isdir(os.path.join(repo_dir, item)) ]
		# list of cloned repositories

	os.chdir('..') # cd out of v3 dir into repo dir

	for repo in repo_list:
		clone_url = stash_api.get_repo_url(repo) # api call to get clone url
		if not repo_clone_url: break # if function returned false
		if not repo == 'v3':
			# if the repository is not v3
			shutil.rmtree('/' + repo) # delete repository before cloning
			char = clone_url.index('@')
			command = clone_url[:char] + ':' + password + clone_url[char:]
			os.system('git clone ' + command)

	os.chdir('v3')


# called by index view
# sets the path to the location of codemaat in order to call maat command
def set_path(maat_dir):
	print("Setting a path for codemaat...")
	os.environ['PATH'] += os.pathsep + maat_dir
	print("Done.")
	print("-" * 60)


# called by index view & index_repo view
# handles command line inputs for cloning a repository
def submit_url(clone_url, password):
	os.chdir('..')
	char = clone_url.index('@')
	command = clone_url[:char] + ':' + password + clone_url[char:]
	clone = os.system('git clone ' + command)
	# temporary message handler for cloning repositories
	clone_status = subprocess.getoutput('git clone ' + command)
	print ("this is the status: " + clone_status)
	if 'Authentication failed' 	in clone_status:
		message = "Authentication failed."
	elif 'already exists' in clone_status:
		message = """Repository already exists. Check the 'Available
		 Repositories' tab."""
	elif 'not found' in clone_status:
		message = """Repository not found. Either it does not exist, or you do 
		not have permission to access it."""
	else:
		message = "Cloning complete. Check the 'Available Repositories tab."
	os.chdir('v3')
	return message


def change_folder(repo_name, date_after, date_before):
	os.system("mkdir csv_files_" + repo_name + "_" + date_after + "_" + date_before)
	os.chdir("csv_files_" + repo_name + "_" + date_after + "_" + date_before)


def directory_return():
	os.chdir("..")


# called by select_folder
# handles command line inputs for creating a logfile
def create_log(repo_name, date_after, date_before, address):
	print("Obtaining repository logs...")
	sys_command = "" # resets to blank
	# first part of command same for any date specification
	sys_command = 'git --git-dir ' + address + ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat'
	sys_command_cloud = 'git --git-dir ' + address + ' log --pretty=format:"%s"'
	#the following commands change depending on date specification
	if not date_after == "" and date_before == "":
		print("date after selected")
		sys_command += ' --after=' + date_after
		sys_command_cloud += ' --after=' + date_after 	
	elif date_after == "" and not date_before == "":
		print("date before selected")
		sys_command += ' --before=' + date_before
		sys_command_cloud += ' --before=' + date_before 	
	elif not date_after == "" and not date_before == "":
		print("date_after and date_before selected")
		sys_command += ' --after=' + date_after + ' --before=' + date_before
		sys_command_cloud += ' --after=' + date_after + ' --before=' + date_before 	
	# last part of command same for any date specification			
	sys_command += ' > logfile_' + repo_name + '_' + date_after + '_' + date_before + '.log'
	sys_command_cloud += ' > cloud_' + repo_name + '_' + date_after + '_' + date_before + '.log'
	os.system(sys_command) # command line call using the updated string
	os.system(sys_command_cloud) 
	# os.system('git --git-dir ' + address + ' log --pretty=format:"%s" > logfile_string.log')
	print("Done.")
	print("-" * 60)


# called by generate_data functions
# helper function to handle command line input for running codemaat
def run_codemaat(analysis_type, analysis_name, repo_name, date_after, date_before):
	os.system("maat -l logfile_" 
		+ repo_name + "_" + date_after + "_" + date_before 
		+ ".log -c git -a " + analysis_type + " > " 
		+ analysis_name + "_" + repo_name + ".csv")


# called by select_folder/select_analysis
# currently only calls run_codemaat on all analyses
def generate_data(address, repo_name, date_after, date_before):
	print("Creating csv files from generated log...")
	time.sleep(1)
	print("Creating repository summary...")
	# run_codemaat('summary', 'summary', repo_name, date_after, date_before)
	# Reports an overview of mined data from git's log file
	print("Creating organizational metrics...")
	# run_codemaat('authors', 'metrics', repo_name, date_after, date_before)
	# Reports the number of authors/revisions made per module
	print("Creating coupling history...")
	# run_codemaat('coupling', 'coupling', repo_name, date_after, date_before)
	# Reports correlation of files that often commit together
	# degree = % of commits where the two files were changed in the same commit
	print("Creating code age summary...")
	# run_codemaat('entity-churn', 'age', repo_name, date_after, date_before)
	# Reports how long ago the last change was made in measurement of months
	print("Creating repository hotspots...")
	# run_codemaat('authors', 'metrics', repo_name, date_after, date_before)
	# os.system("cloc ../../" + repo_name + " --unix --by-file --csv --quiet --report-file=" 
	# 	+ "hotspots_" + repo_name + ".csv")
	# merge_csv(repo_name)
	print("Done. Check your current folder for your files.")
	print("-" * 60)


# NOTE: currently NOT IN USE
def generate_data_summary(address, repo_name, date_after, date_before):
	time.sleep(1)
	print("Creating repository summary...")
	run_codemaat('summary', 'summary', repo_name, date_after, date_before)
	print("-" * 60)

# NOTE: currently NOT IN USE
def generate_data_hotspot(address, repo_name, date_after, date_before):
	time.sleep(1)
	print("Creating repository hotspots...")
	run_codemaat('authors', 'metrics', repo_name, date_after, date_before)
	os.system("cloc ../../" + repo_name + " --unix --by-file --csv --quiet --report-file=" 
		+ "hotspots_" + repo_name + ".csv")
	merge_csv(repo_name)
	print("-" * 60)

# NOTE: currently NOT IN USE
def generate_data_metrics(address, repo_name, date_after, date_before):
	time.sleep(1)
	print("Creating organizational metrics...")
	run_codemaat('authors', 'metrics', repo_name, date_after, date_before)
		# Reports the number of authors/revisions made per module
	print("-" * 60)

# NOTE: currently NOT IN USE
def generate_data_coupling(address, repo_name, date_after, date_before):
	time.sleep(1)
	print("Creating coupling history...")
	run_codemaat('coupling', 'coupling', repo_name, date_after, date_before)
	print("-" * 60)

# NOTE: currently NOT IN USE
# called by select_folder
# reads user selection of analyses 
# calls helper functions that run codemaat 
# FIX: currently does not read multiple selections
def select_analysis(address, repo, from_date, to_date):
	if request.form['checkbox'] == "summary":
		print ("button: " + request.form['checkbox'])
		generate_data_summary(address, repo, from_date, to_date)
	if request.form['checkbox'] == "hotspots":
		print ("button: " + request.form['checkbox'])
		generate_data_hotspot(address, repo, from_date, to_date)
	if request.form['checkbox'] == "metrics":
		print ("button: " + request.form['checkbox'])
		generate_data_metrics(address, repo, from_date, to_date)
	if request.form['checkbox'] == "coupling":
		print ("button: " + request.form['checkbox'])
		generate_data_coupling(address, repo, from_date, to_date)
	if request.form['checkbox'] == "0":
		print("none selected- button: " + request.form['checkbox'])
		generate_data(address, repo, from_date, to_date)


# called by index view
# sets the address where csv files are/will be located
# handles switching between directories
# calls helper functions that handle folder, logfile, & codemaat
def select_folder(repo_dir, repo, from_date, to_date):
	print("1: " + os.getcwd())
	root_dir = os.getcwd() + '/csv_files_' + repo + "_" + from_date + "_" + to_date
		# root_dir is the complete address of csv folder for chosen repo

	if(os.path.exists(root_dir)):
		# if the csv folder for the chosen repo exists in 'v3'
		print("folder exists: " + root_dir)
		os.chdir("csv_files_" + repo + "_" + from_date + "_" + to_date)
			# switch to that folder
	else:
		# if that csv folder doesn't exist
		print("creating folder: " + root_dir)
		change_folder(repo, from_date, to_date) 
			# create that folder and switch to it

	address = repo_dir + repo + '/.git'

	create_log(repo, from_date, to_date, address)
		# while in the csv folder of chosen repo, create log file
	print("2: " + os.getcwd())

	# select_analysis(address, repo, from_date, to_date)
	generate_data(address, repo, from_date, to_date)
	directory_return() # go back to parent directory ('v3')
	print("3: " + os.getcwd())
	flash('Analysis complete.')
	return root_dir


# called by result view
# reads opened csv file
# creates a list of the headers, and a dictionary of each row
# returns the list of headers, and a list of the dictionaries
def parse_csv(uploaded_file):
	reader = csv.reader(uploaded_file)
	data_dict = []
	key_array = []

	for i, row in enumerate(reader):
		row_array = {}
		if i == 0:
			key_array = row
		else:
			for j, key in enumerate(key_array):
				row_array[key] = row[j]
			data_dict.append(row_array)

	return (data_dict, key_array)


# called by generate_data/generate_data_hotspot
# collects num of revs from metrics.csv & lines from hotspots.csv
# merges them together with respective modules
# re-writes hotspots.csv w/ merged data
def merge_csv(repo_name):
	lines_array = []
	merge_array = []

	try:
		with open("hotspots_" + repo_name + ".csv") as lines_file:
			lines_reader = csv.DictReader(lines_file)
			for row in lines_reader:
				lines_array.append({'entity': row['filename'], 'lines': row['code']})
	except IOError:
		print("file not found")
		return

	with open("metrics_" + repo_name + ".csv", "rt") as rev_file:
		revs_reader = csv.DictReader(rev_file)
		for row in revs_reader:
			for module in lines_array:
				if row['entity'] in module['entity']:
					merge_array.append({
						'entity': row['entity'], 
						'n-revs': row['n-revs'], 
						'lines': module['lines']})

	with open("hotspots_" + repo_name + ".csv", "wt") as hotspot_file:
		fieldnames = ['entity', 'n-revs', 'lines']
		writer = csv.DictWriter(hotspot_file, fieldnames=fieldnames) 
		writer.writeheader()
		for row in merge_array:
			writer.writerow(row)

# stop_words = ['merge', 'merged', 'feature', "'feature'", 'and', 'or']
# called by get_word_frequency
# filters out non-significant words
stop_words = get_stop_words('en')
def redundant_word(word):
	if word in stop_words:
		return True
	elif word in ('1)', '2)', '3)', '4)', '5)'):
		return True
	elif word[:4] in ('http'):
		return True
	elif word[:1] in ('1', '2', '3', '4', '5', '=', '~', '*', '&', 
					  ':', '+', '|', '*/', '/**', '(', ')', 'l', '-'):
		return True
	else: 
		return False

# called by get_word_frequency
# iterates over word_list & checks for given word within each dict
def word_exists(word, word_list):
	for word_pair in word_list:
		if word.lower() == word_pair['text']:
			word_pair['size'] += 1
			return True

# CURRENTLY NOT IN USE
# aqcuires list of all words from commit messages
# creates a list of dictionaries of words paired with frequency of occurrence
def get_word_frequency(logfile):
	log_list = logfile.read().split()
	logfile.close()

	word_list = []

	for word in log_list:
		if redundant_word(word.lower()): continue
		else:
			if not word_list:
				word_list.append({'text': word.lower(), 'size': 1})
			else:
				if word_exists(word, word_list): continue
				else:
					word_list.append({'text': word.lower(), 'size': 1})

	return(word_list)


if __name__ == '__main__':
	# print (folder_list)
	# print (project_list)
	# print(project_key)
	get_word_frequency()