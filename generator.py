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


# called by refresh_repos
# returns a list of directories within the specified path
def get_list_of_dirs(path):
	dir_list = [ item for item in os.listdir(path) 
			if os.path.isdir(os.path.join(path, item)) ]
		# list of cloned repositories

	return dir_list


def get_repo_list(repo_dir, dir_list):
	repo_list = []
	os.chdir(repo_dir) 
	for repo in dir_list:
		os.chdir(repo)
		# for each repo, go into it & get timetag; append name and tag to list
		try:
			with open('timetag.txt', 'rt') as timetag:
				current_datetime = timetag.read()
				repo_list.append(repo + '|' + current_datetime)
		except IOError:
			repo_list.append(repo)
		os.chdir('..') # go back to repo_dir

	return repo_list


def add_datetime(repo):
	os.chdir(repo) # assuming in repo_dir, cd into repo
	with open('timetag.txt', 'wt') as timetag:
		d = str(datetime.now()).split('.') # date/time in string
		timetag.write(d[0]) # add a textfile with current date/time w/out ms
	os.chdir('..') # got back to repo_dir


def refresh_single_repo(repo_dir, repo):
	clone_url = stash_api.get_repo_url(repo, 'http') 
			# api call to get http clone url
	clone_cmd = get_clone_command(clone_url, settings.password)
		# currently using http clone url w/ password
	if not clone_url: return # if function returned false
	else:
		# if the repository is not v3
		shutil.rmtree(repo) # delete repository
		os.system('git clone ' + clone_cmd) # re-clone the repository
			# CHANGE CLONE_CMD TO CLONE_URL ONCE SSH WORKS
		add_datetime(repo) # make timetag file
		manage_csv_folder(repo_dir, repo, '', '') # re-run codemaat
		os.chdir(repo_dir) # go back to repo directory


# called by visualizer at timed intervals
# updates already cloned repositories
def refresh_repos(repo_dir):
	repo_list = get_list_of_dirs(repo_dir)

	os.chdir(repo_dir) # cd out of v3 dir into repo dir
	print(os.getcwd())

	for repo in repo_list:
		if repo == 'v3': continue
		refresh_single_repo(repo_dir, repo)
		# clone_url = stash_api.get_repo_url(repo, 'http') 
		# 	# api call to get http clone url
		# clone_cmd = get_clone_command(clone_url, settings.password)
		# 	# currently using http clone url w/ password
		# if not clone_url: continue # if function returned false
		# if repo == 'v3': continue
		# else:
		# 	# if the repository is not v3
		# 	shutil.rmtree(repo) # delete repository
		# 	os.system('git clone ' + clone_cmd) # re-clone the repository
		# 		# CHANGE CLONE_CMD TO CLONE_URL ONCE SSH WORKS
		# 	add_datetime(repo) # make timetag file
		# 	manage_csv_folder(repo_dir, repo, '', '') # re-run codemaat
		# 	os.chdir(repo_dir) # go back to repo directory

	os.chdir(settings.v3_dir) # cd back into v3
	print(os.getcwd())


# called by index view to set path for codemaat
# sets the path to the passed in address
def set_path(path):
	print("Setting a path to " + path)
	os.environ['PATH'] += os.pathsep + path
	print("Done.")
	print("-" * 60)


# called by visualizer index view
# parses the user given clone url and password; returns combined http url
def get_clone_command(clone_url, password):
	char = clone_url.index('@') # string index of '@'
	command = clone_url[:char] + ':' + password + clone_url[char:]
		# add password to the string right before the '@'
	return command


# called by visualizer index view
# calls git clone command with an appropriate url
def clone_repo(clone_url):
	os.chdir(settings.repo_dir)
	if 'http' in clone_url:
		clone_cmd = get_clone_command(clone_url, settings.password)
	else: clone_cmd = clone_url
	os.system('git clone ' + clone_cmd)
	# repo_name = clone_url.split('/').pop().split('.')[0]
	add_datetime(clone_url.split('/').pop().split('.')[0])
	os.chdir(settings.v3_dir)


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
	#files to be ignored
	extensions = ('.png', '.csv', '.jpg', '.svg', '.html', '.less', '.swf',
	 '.spec', '.md', '.ignore', '.ttf', '.min')

	file_list = []
	csv_list = []
	git_list = []

	# get the log id of the first and latest commit in the repository
	first_id = subprocess.getoutput('git --git-dir ' + address 
		+ ' log --pretty=format:"%h" --no-patch --reverse | head -1')
	last_id = subprocess.getoutput('git --git-dir ' + address 
		+ ' log --pretty=format:"%h" --no-patch | head -1')
	# gets the list of commit IDs and their dates
	values = subprocess.getoutput('git --git-dir ' + address 
		+ ' log --pretty=format:"%h %ad" --date=short --no-patch --reverse')

	for item in values.splitlines():
		git_list.append(item)


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
		os.system('python2 ' + settings.v3_dir + '/git_complexity_trend.py --start ' 
			+ first_id + ' --end ' + last_id + ' --file ' + split_path[1] + ' > ' 
			+ settings.csv_dir  + folder_name + '/complex_' 
			+ os.path.basename(os.path.normpath(split_path[1])) + '.csv')


	os.chdir(settings.csv_dir + folder_name)

	for file in glob.glob("*.csv"):
		csv_list.append(file)

	#appends csv files together into one	
	os.system('csvcat --skip-headers ' + (' '.join(csv_list)) + ' > ' 
		+ 'complex_' + repo + '.csv')

	#adds date column to csv file
	with open('complex_' + repo + '.csv','r') as csvinput:
		 with open('complexity_' + repo + '.csv', 'w') as csvoutput:
			 csv_write = csv.writer(csvoutput, lineterminator='\n')
			 csv_reader = csv.reader(csvinput)

			 all = []
			 row = next(csv_reader)
			 row.append('date')
			 all.append(row)

			 for row in csv_reader:
				 for item in git_list:
					 if item.split(' ')[0] in row:
						 row.append(item.split(' ')[1])
						 all.append(row)
			 csv_write.writerows(all)

	for file in glob.glob("complex_*"):
		os.remove(file)


# called by index view
# sets the address where csv files are/will be located
# handles switching between directories
# calls helper functions that handle folder, logfile, & codemaat
def manage_csv_folder(repo_dir, repo, from_date, to_date):
	print("1: " + os.getcwd())
	folder_name = "csv_files_" + repo + "_" + from_date + "_" + to_date
	csv_path = settings.csv_dir + folder_name
		# csv_path is the complete address of csv folder for chosen repo

	if not os.path.exists(csv_path):
		# if that csv folder doesn't exist
		print("creating folder: " + csv_path)
		os.system("mkdir " + csv_path)
		os.chdir(csv_path) # switch to csv folder of chosen repo
		print("2: " + os.getcwd())
		repo_address = repo_dir + repo + '/.git'
		create_log(repo, from_date, to_date, repo_address) # make logfile

		generate_data_summary(repo, from_date, to_date)
		generate_data_metrics(repo, from_date, to_date)
		generate_data_coupling(repo, from_date, to_date)
		generate_data_age(repo, from_date, to_date)
		generate_data_hotspots(repo, from_date, to_date)

		os.chdir(settings.v3_dir)
	else: print("folder exists: " + csv_path)
	print("3: " + os.getcwd())
	# flash('Analysis complete.')
	# return csv_path


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
	data_dict = [] # list of dictionaries, one dict for each row
	key_list = [] # list of row headers / keys

	for i, row in enumerate(reader):
		temp_dict = {}
		if i == 0:
			# if first row of file, fill key_list with headers
			key_list = row
		else:
			# fill temp dict with each value in the row
			if not ignore_module(row[0]):
				for j, key in enumerate(key_list):
					temp_dict[key] = row[j] # pair respective header w/ value
				data_dict.append(temp_dict)

	return (data_dict, key_list)


# called by merge_csv
# parses module names/lines of code from lines.csv
def get_lines_list(repo_name):
	lines_list = [] # list of dictionaries, one dict for each row

	try:
		with open("lines_" + repo_name + ".csv") as lines_file:
			lines_reader = csv.DictReader(lines_file)
			for row in lines_reader:
				# create a dict with name and num lines; add it to list
				lines_list.append({'entity': row['filename'], 
									'lines': row['code']})
	except IOError:
		print("file not found")

	return lines_list


# called by merge_csv
# combines data from lines.csv with metrics.csv
def get_merge_list(repo_name, lines_list):
	merge_list = [] # list of dictionaries, one dict for each row

	try:
		with open("metrics_" + repo_name + ".csv", "rt") as revs_file:
			revs_reader = csv.DictReader(revs_file)
			for row in revs_reader:
				# for each entity in metrics, look for it in lines_list
				for module in lines_list:
					if row['entity'] in module['entity']:
						# add new dict w/ name, revs, and lines to merge_list
						merge_list.append({
							'entity': row['entity'], 
							'n-revs': row['n-revs'], 
							'lines': module['lines']})
	except IOError:
		print("file not found")

	return merge_list


# called by generate_data/generate_data_hotspot
# retrieves combined data from lines.csv & merge.csv
# writes combined data into new hotspots.csv file
def merge_csv(repo_name):
	lines_list = get_lines_list(repo_name)
	merge_list = get_merge_list(repo_name, lines_list)

	try:
		with open("hotspots_" + repo_name + ".csv", "wt") as hotspot_file:
			# create a new csv file
			fieldnames = ['entity', 'n-revs', 'lines'] # use these as headers
			writer = csv.DictWriter(hotspot_file, fieldnames=fieldnames)
			writer.writeheader() # write fieldnames into header row
			for row in merge_list:
				# write each row from merge_list into new csv file
				writer.writerow(row)
	except IOError:
		print("file not found")
		return


#define stop_words as a global for efficiency
stop_words = get_stop_words('en')
def parse_word(stem, word, word_list):
	if word in stop_words or len(word) == 1:
		return

	entry = [x for x in word_list if x["stem"] == stem]
	if entry:
		entry[0]['freq'] += 1
		if word in entry[0]['text']:
			entry[0]['text'][word] += 1
		else:
			entry[0]['text'][word] = 1
	else:
		word_list.append({'stem': stem, 'text':{ word: 1 } , 'freq': 1 })


# aqcuires list of all words from commit messages
# creates a list of dictionaries of words paired with frequency of occurrence
def get_word_frequency(logfile):
	log_list = logfile.read().split()
	logfile.close()

	word_list = []
	stemmer = LancasterStemmer()

	for word in log_list:
		# remove unwanted leading and trailing characters
		word = word.strip("\"'/;:?{}[]!.,()").lower()
		stem = stemmer.stem(word) # stemming

		parse_word(stem,word,word_list)

	# Sort and return selection of the word_list
	sorted_word_list = sorted(word_list, key = lambda x: x['freq'], reverse = True)

	textFreqPairs = []
	for word in sorted_word_list[:100]:
		key = max(word['text'].keys(), key=(lambda k: word['text'][k]))
		textFreqPairs.append({'text': key, 'freq': word['freq']})
	return textFreqPairs


# retrieved from: http://stackoverflow.com/questions/3424899/
# 	+ whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
def monthdelta(date, delta):
	m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
	if not m: m = 12
	d = min(date.day, [31,
		29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
	return date.replace(day=d,month=m, year=y)

def get_prev_date():
	for m in range(-2, -1):
		month_string = str(monthdelta(datetime.now(), m))
	previous_date = ((month_string)[:10])

	return previous_date

# if __name__ == '__main__':
	# print("hello")

