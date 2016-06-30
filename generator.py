import csv
import os
import fnmatch
import glob
import subprocess
from flask import request, flash
from stop_words import get_stop_words
import stash_api
import settings
import shutil
from nltk.stem.lancaster import LancasterStemmer
from datetime import datetime


# switches working directory to passed in address
# NOTE: might be pointless; get rid of it?
def change_directory(path):
	if not os.getcwd() == path:
		os.chdir(path)
	else: return False


# called by visualizer at timed intervals
# updates already cloned repositories
def refresh_repos(repo_dir):
	repo_list = [ item for item in os.listdir(repo_dir) 
			if os.path.isdir(os.path.join(repo_dir, item)) ]
		# list of cloned repositories

	os.chdir(repo_dir) # cd out of v3 dir into repo dir
	print(os.getcwd())

	for repo in repo_list:
		clone_url = stash_api.get_repo_url(repo) # api call to get clone url
		if not clone_url: continue # if function returned false
		if repo == 'v3': continue
		else:
			# if the repository is not v3
			shutil.rmtree(repo) # delete repository before cloning
			os.system('git clone ' + clone_url)

	os.chdir(settings.v3_dir) # cd back into v3
	print(os.getcwd())


# called by index view to set path for codemaat
# sets the path to the passed in address
def set_path(path):
	print("Setting a path to " + path)
	os.environ['PATH'] += os.pathsep + path
	print("Done.")
	print("-" * 60)


# calls git clone command with an appropriate url
def clone_repo(clone_url):
	os.chdir(settings.repo_dir)
	os.system('git clone ' + clone_url)
	os.chdir(settings.v3_dir)


# parses the user given clone url and password; returns combined http url
def get_clone_command(clone_url, password):
	char = clone_url.index('@')
	command = clone_url[:char] + ':' + password + clone_url[char:]
	return command


# called by index view to generate message
# FIX: currently cd's into repo_dir and re-clones the repo
# 	causing the message to be "already exists"
def get_status_message(clone_url):
	os.chdir(settings.repo_dir)
	# temporary message handler for cloning repositories
	clone_status = subprocess.getoutput('git clone ' + clone_url)
	print ("this is the status: " + clone_status)
	if 'Authentication failed' 	in clone_status:
		message = "Authentication failed."
	elif 'already exists' in clone_status:
		message = """Repository exists. Check the 'Available
		 Repositories' tab."""
	elif 'not found' in clone_status:
		message = """Repository not found. Either it does not exist, or you do 
		not have permission to access it."""
	else:
		message = "Cloning complete. Check the 'Available Repositories tab."
	os.chdir(settings.v3_dir)
	return message


# called by generate_data functions
# helper function to handle command line input for running codemaat
def run_codemaat(analysis_type, analysis_name, repo_name, from_date, to_date):
	os.system("maat -l logfile_" 
		+ repo_name + "_" + from_date + "_" + to_date 
		+ ".log -c git -a " + analysis_type + " > " 
		+ analysis_name + "_" + repo_name + ".csv")


# NOTE: currently NOT IN USE
# called by manage_csv_folder/select_analysis
# currently only calls run_codemaat on all analyses
def generate_data(address, repo_name, from_date, to_date):
	print("Creating csv files from generated log...")
	print("Creating repository summary...")
	run_codemaat('summary', 'summary', repo_name, date_after, date_before)
	# # Reports an overview of mined data from git's log file
	print("Creating organizational metrics...")
	run_codemaat('authors', 'metrics', repo_name, date_after, date_before)
	# # Reports the number of authors/revisions made per module
	print("Creating coupling history...")
	run_codemaat('coupling', 'coupling', repo_name, date_after, date_before)
	# # Reports correlation of files that often commit together
	# # degree = % of commits where the two files were changed in the same commit
	print("Creating code age summary...")
	run_codemaat('entity-churn', 'age', repo_name, date_after, date_before)
	# # Reports how long ago the last change was made in measurement of months
	print("Creating repository hotspots...")
	run_codemaat('authors', 'metrics', repo_name, date_after, date_before)
	os.system("cloc ../../" + repo_name + " --unix --by-file --csv --quiet --report-file=lines_" + repo_name + ".csv")
	merge_csv(repo_name)
	print("Done. Check your current folder for your files.")
	print("-" * 60)


# reports an overview of mined data from git's log file
def generate_data_summary(repo_name, from_date, to_date):
	print("Creating repository summary...")
	run_codemaat('summary', 'summary', repo_name, from_date, to_date)
	print("-" * 60)

# reports the number of authors/revisions made per module
def generate_data_metrics(repo_name, from_date, to_date):
	print("Creating organizational metrics...")
	run_codemaat('authors', 'metrics', repo_name, from_date, to_date)
		# Reports the number of authors/revisions made per module
	print("-" * 60)

# reports correlation of files that often commit together
def generate_data_coupling(repo_name, from_date, to_date):
	print("Creating coupling history...")
	run_codemaat('coupling', 'coupling', repo_name, from_date, to_date)
	print("-" * 60)

# reports number of lines added vs deleted over the chosen date range
def generate_data_age(repo_name, from_date, to_date):
	print("Creating code age summary")
	run_codemaat('entity-churn', 'age', repo_name, from_date, to_date)
	print("-" * 60)

# runs cloc to retrieve number of lines of code
# merges with metrics data to show hotspots
def generate_data_hotspots(repo_name, from_date, to_date):
	print("Creating repository hotspots...")
	if not os.path.isfile("metrics_" + repo_name + ".csv"):
		print("Creating metrics...")
		run_codemaat('authors', 'metrics', repo_name, from_date, to_date)
	os.system("cloc " + settings.repo_dir + repo_name 
		+ " --unix --by-file --csv --quiet --report-file=" 
		+ "lines_" + repo_name + ".csv")
	merge_csv(repo_name)
	print("-" * 60)


# NOTE: currently NOT IN USE
# called by manage_csv_folder
# reads user selection of analyses & calls helper functions that run codemaat 
# FIX: currently does not read multiple selections
def select_analysis(address, repo, from_date, to_date):
	if request.form['checkbox'] == "summary":
		print ("button: " + request.form['checkbox'])
		generate_data_summary(address, repo, from_date, to_date)
	if request.form['checkbox'] == "hotspots":
		print ("button: " + request.form['checkbox'])
		generate_data_hotspots(address, repo, from_date, to_date)
	if request.form['checkbox'] == "metrics":
		print ("button: " + request.form['checkbox'])
		generate_data_metrics(address, repo, from_date, to_date)
	if request.form['checkbox'] == "coupling":
		print ("button: " + request.form['checkbox'])
		generate_data_coupling(address, repo, from_date, to_date)
	if request.form['checkbox'] == "0":
		print("none selected- button: " + request.form['checkbox'])
		generate_data(address, repo, from_date, to_date)


# called by manage_csv_folder
# handles command line inputs for creating a logfile
def create_log(repo_name, from_date, to_date, address):
	print("Obtaining repository logs...")
	sys_command = "" # resets to blank
	# first part of command same for any date specification
	sys_command = ('git --git-dir ' + address 
		+ ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat')
	sys_command_cloud = 'git --git-dir ' + address + ' log --pretty=format:"%s"'
	#the following commands change depending on date specification
	if not from_date == "" and to_date == "":
		sys_command += ' --after=' + from_date
		sys_command_cloud += ' --after=' + from_date 	
	elif from_date == "" and not to_date == "":
		sys_command += ' --before=' + to_date
		sys_command_cloud += ' --before=' + to_date 	
	elif not from_date == "" and not to_date == "":
		sys_command += ' --after=' + from_date + ' --before=' + to_date
		sys_command_cloud += ' --after=' + from_date + ' --before=' + to_date 	
	# last part of command same for any date specification			
	sys_command += (' > logfile_' 
		+ repo_name + '_' + from_date + '_' + to_date + '.log')
	sys_command_cloud += (' > cloud_' 
		+ repo_name + '_' + from_date + '_' + to_date + '.log')
	os.system(sys_command) # command line call using the updated string
	os.system(sys_command_cloud) 
	print("Done.")
	print("-" * 60)


#obtains complexity history of entire repository, regardless of date selected
#can take a long time (up to 3 min)when running on large repositories
#requires the 'csvcat' python package
def create_complexity_files(repo, address, from_date, to_date):
	folder_name = "csv_files_" + repo + "_" + from_date + "_" + to_date
	extensions = ('.png', '.csv', '.jpg', '.svg', '.html', '.less', '.swf',
	 '.spec', '.md', '.ignore', '.ttf')
	#files to be ignored
	file_list = []
	csv_list = []

	# get the log id of the first and latest commit in the repository
	first_id = subprocess.getoutput('git --git-dir ' + address 
		+ ' log --pretty=format:"%h" --no-patch --reverse | head -1')
	last_id = subprocess.getoutput('git --git-dir ' + address 
		+ ' log --pretty=format:"%h" --no-patch | head -1')

	for root, dirs, files in os.walk(settings.repo_dir + repo):
		if '.git' in dirs:
			dirs.remove('.git')
		for file in files:
			if file.endswith(extensions):
				continue
			file_list.append(os.path.join(root, file))

	os.chdir(settings.repo_dir + repo)

	#runs complexity analysis script on each file in the repository
	for file in file_list:
		split_path = file.split(repo + '/')
		os.system('python ' + settings.v3_dir + '/git_complexity_trend.py --start ' 
			+ first_id + ' --end ' + last_id + ' --file ' + split_path[1] + ' > ' 
			+ settings.csv_dir  + folder_name + '/complex_' 
			+ os.path.basename(os.path.normpath(split_path[1])) + '.csv')

	os.chdir(settings.csv_dir + folder_name)

	for file in glob.glob("*.csv"):
		csv_list.append(file)

	#appends csv files together into one	
	os.system('csvcat --skip-headers ' + (' '.join(csv_list)) + ' > ' 
		+ 'complexity_' + repo + '.csv')

	for file in glob.glob("complex_*"):
		os.remove(file)


# called by index view
# sets the address where csv files are/will be located
# handles switching between directories
# calls helper functions that handle folder, logfile, & codemaat
def manage_csv_folder(repo_dir, repo, from_date, to_date):
	# print("1: " + os.getcwd())
	folder_name = "csv_files_" + repo + "_" + from_date + "_" + to_date
	csv_path = settings.csv_dir + folder_name
		# csv_path is the complete address of csv folder for chosen repo

	if not os.path.exists(csv_path):
		# if that csv folder doesn't exist
		print("creating folder: " + csv_path)
		os.system("mkdir " + csv_path)
	else:
		print("folder exists: " + csv_path)

	repo_address = repo_dir + repo + '/.git'

	os.chdir(csv_path) # switch to csv folder of chosen repo
	# print("2: " + os.getcwd())
	create_log(repo, from_date, to_date, repo_address) # make logfile

	create_complexity_files(repo, repo_address, from_date, to_date)
	os.chdir(csv_path)

	# generate_data_summary(repo, from_date, to_date)
	# generate_data_metrics(repo, from_date, to_date)
	# generate_data_coupling(repo, from_date, to_date)
	# generate_data_age(repo, from_date, to_date)
	# generate_data_hotspots(repo, from_date, to_date)

	os.chdir(settings.v3_dir)
	# print("3: " + os.getcwd())
	flash('Analysis complete.')
	return csv_path


# called by parse_csv
# checks is passed in string is in list of modules to be ignored
def ignore_module(entity):
	ignore_list = ['bower.json', '.gitignore', 'README.md']
		# list to be expanded
	if entity in ignore_list: return True
	else:
		return False


# called by result view
# reads opened csv file
# returns a list of the headers, and a dictionary of each row
def parse_csv(uploaded_file):
	reader = csv.reader(uploaded_file)
	data_dict = []
	key_array = []

	for i, row in enumerate(reader):
		row_array = {}
		if i == 0:
			key_array = row
		else:
			if not ignore_module(row[0]):
				for j, key in enumerate(key_array):
					row_array[key] = row[j]
				data_dict.append(row_array)

	return (data_dict, key_array)


# called by generate_data/generate_data_hotspot
# collects num of revs from metrics.csv & lines from lines.csv
# merges them together with respective modules into hotspots.csv
def merge_csv(repo_name):
	lines_array = []
	merge_array = []

	try:
		with open("lines_" + repo_name + ".csv") as lines_file:
			lines_reader = csv.DictReader(lines_file)
			for row in lines_reader:
				lines_array.append({'entity': row['filename'], 
									'lines': row['code']})

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
	except IOError:
		print("file not found")
		return


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
def word_exists(stem, word, word_list):
	for word_pair in word_list:
		if stem == word_pair['stem']:
			if len(word) < len(word_pair['text']):
				word_pair['text'] = word
			word_pair['freq'] += 1
			return True


# aqcuires list of all words from commit messages
# creates a list of dictionaries of words paired with frequency of occurrence
def get_word_frequency(logfile):
	log_list = logfile.read().split()
	logfile.close()

	word_list = []
	stemmer = LancasterStemmer()

	for word in log_list:
		# Remove unwanted leading and trailing characters
		word = word.strip("\"'/;:?{}[]!.,()").lower()
		#Stemming
		stem = stemmer.stem(word)

		if redundant_word(word) or len(word) == 1 : continue
		else:
			if not word_list:
				word_list.append({'stem': stem, 'text': word, 'freq': 1})
			else:
				if word_exists(stem, word, word_list): continue
				else:
					word_list.append({'stem': stem, 'text': word, 'freq': 1})
	# Return the top 50 ocurring words
	return(sorted(word_list, key = lambda x: x['freq'], reverse = True)[:100])


def monthdelta(date, delta):
	m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
	if not m: m = 12
	d = min(date.day, [31,
		29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
	return date.replace(day=d,month=m, year=y)

for m in range(-2, -1):
	time = str (monthdelta(datetime.now(), m))
previous_date=((time)[:10])

# if __name__ == '__main__':
	# print (folder_list)
	# print (project_list)
	# print(project_key)
	# get_word_frequency()

