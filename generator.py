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

repo_dir = settings.repo_dir




# called by refresh_repos
def get_dir_list(path):
	dir_list = [ item for item in os.listdir(path)
			if os.path.isdir(os.path.join(path, item)) ]
		# if 'path/item' is valid address, add item to list
	return dir_list


# called by get_repo_list, refresh_single_repo
# uses git log to get first & last commit dates
def get_commit_dates(repo):
	first_date = subprocess.getoutput('git --git-dir '
		+ os.path.join(repo_dir, repo, '.git')
		+ ' log --pretty=format:"%ad" --no-patch --date=short --reverse | head -1')
	last_date = subprocess.getoutput('git --git-dir '
		+ os.path.join(repo_dir, repo, '.git')
		+ ' log --pretty=format:"%ad" --date=short --no-patch | head -1')
	return (first_date, last_date)


# called by: index view
# params: path of repo directory, list of repo folders
def get_repo_list(dir_list):
	repo_list = []
	for repo in dir_list:
		first_date, last_date = get_commit_dates(repo)
		try:
			filename = os.path.join(repo_dir, repo, 'timetag.txt')
			with open(filename, 'rt') as timetag:
				latest_datetime = timetag.read()
				repo_list.append(repo + '|'
					+ latest_datetime + '|' + first_date + '|' + last_date)
		except IOError:
			repo_list.append(repo + '|' + ' ' + '|' + first_date + '|' + last_date)
	return repo_list


# called by: refresh_single_repo, clone_repo
def add_datetime(folder_path):
	with open(os.path.join(folder_path, 'timetag.txt'), 'wt') as timetag:
		d = str(datetime.now()).split('.')[0].split(' ') # date in string
		timetag.write(d[0]) # add a textfile with current date w/out ms or time


# called by: refresh_repos, index view
def refresh_single_repo(repo):
	clone_url = stash_api.get_repo_url(repo, 'http')
	if not clone_url: return # if function returned false
	else:
		shutil.rmtree(os.path.join(repo_dir, repo)) # delete repository
		clone_repo(clone_url, repo_dir, settings.password)
		from_date, to_date = get_commit_dates(repo)
		csv_path = os.path.join(settings.csv_dir,
			repo + "_" + from_date + "_" + to_date)
		process_log(repo, from_date, to_date, csv_path)


# called by: visualizer at timed intervals
# updates already cloned repositories
def refresh_repos():
	repo_list = get_dir_list()
	for repo in repo_list:
		refresh_single_repo(repo)

# Check repo clone if it doesn't exist and re-clone if it is old
def repo_check_and_update(repo_name, proj_key, to_date):
	repo_list = get_repo_list(get_dir_list(repo_dir))
	available_repo = [ repo for repo in repo_list
		if repo.split('|')[0] == repo_name ]
	remote_last_commit = stash_api.get_repo_timestamp(proj_key,
		repo_name, 'http', '1')[0]

	if available_repo == []:
		# Repo Doesn't exist locally so clone
		repo_url = stash_api.get_repo_url(repo_name, 'http')
		clone_repo(repo_url, repo_dir, settings.password)
	elif (remote_last_commit > available_repo[0].split('|')[1].split(" ")[0] < to_date):
		# Local copy is old so refresh
		refresh_single_repo(repo_name)


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
def clone_repo(clone_url, location, password):
	if 'http' in clone_url:
		# if using http url, apply password to url
		clone_cmd = get_clone_command(clone_url, password)
	else: clone_cmd = clone_url
	repo = clone_url.split('/').pop().split('.')[0]
	os.system('git clone ' + clone_cmd + ' ' + os.path.join(location, repo))
	add_datetime(os.path.join(location, repo))


# called by index view to generate message
# FIX: currently cd's into repo_dir and re-clones the repo
# 	causing the message to be "already exists"
def get_status_message(clone_url):
	os.chdir(repo_dir)
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
	os.system("cloc " + repo_dir + repo_name
		+ " --unix --by-file --csv --quiet --report-file="
		+ "lines_" + repo_name + ".csv")
	merge_csv(repo_name)
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
		+ log_type + '_' + repo_name + '_' + from_date + '_' + to_date + '.log')
	os.system(sys_command)
	print("Done.")
	print("-" * 60)


#obtains complexity history of entire repository, regardless of date selected
#can take a long time (up to 3 min)when running on large repositories
#requires the 'csvcat' python package
def create_complexity_files(repo, address, from_date, to_date):
	folder_name = repo + "_" + from_date + "_" + to_date
	#files to be ignored
	extensions = ('.png', '.csv', '.jpg', '.svg', '.html', '.less', '.swf',
	 '.spec', '.md', '.ignore', '.ttf', '.min', '.css')

	file_list = []
	csv_list = []
	git_list = []

	# get the log id of the first and latest commit in the repository
	first_id = subprocess.getoutput('git --git-dir ' + address
		+ ' log --pretty=format:"%h" --no-patch --reverse | head -1')
	last_id = subprocess.getoutput('git --git-dir ' + address
		+ ' log --pretty=format:"%h" --no-patch | head -1')
	# gets the list of commit IDs and their dates
	git_values = subprocess.getoutput('git --git-dir ' + address
		+ ' log --pretty=format:"%h %ad" --date=short --no-patch --reverse')

	for item in git_values.splitlines():
		git_list.append(item)


	for root, dirs, files in os.walk(repo_dir + repo):
		if '.git' in dirs:
			dirs.remove('.git')
		for file in files:
			if file.endswith(extensions):
				continue
			file_list.append(os.path.join(root, file))

	os.chdir(os.path.join(repo_dir, repo))

	#runs complexity analysis script on each file in the repository
	for file in file_list:
		split_path = file.split(repo + '/')
		os.system('python2 ' + settings.v3_dir + '/git_complexity_trend.py --start '
			+ first_id + ' --end ' + last_id + ' --file ' + split_path[1] + ' > '
			+ settings.csv_dir  + folder_name + '/complex_'
			+ os.path.basename(os.path.normpath(split_path[1])) + '.csv')


	os.chdir(os.path.join(settings.csv_dir, folder_name))

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

	os.chdir(setting.v3_dir)


# called by: manage_csv_folder, refresh_repos
# generates log file and runs codemaat
def process_log(repo, from_date, to_date, csv_path):
	if not os.path.isdir(csv_path): os.system("mkdir " + csv_path)
		# if the csv_folder doesn't exist, make it
	os.chdir(csv_path)
	# cd into the folder and create logs and csv files
	repo_address = os.path.join(repo_dir, repo, '.git')
	create_log('logfile', repo, from_date, to_date, repo_address)
	create_log('cloud', repo, from_date, to_date, repo_address)

	generate_data_summary(repo, from_date, to_date)
	generate_data_metrics(repo, from_date, to_date)
	generate_data_coupling(repo, from_date, to_date)
	generate_data_age(repo, from_date, to_date)
	generate_data_hotspots(repo, from_date, to_date)

	os.chdir(settings.v3_dir)


# called by: index view
# sets the address where csv files are/will be located
# calls helper functions that handle folder, logfile, & codemaat
def manage_csv_folder(repo, from_date, to_date):
	folder_name = repo + "_" + from_date + "_" + to_date
	csv_path = os.path.join(settings.csv_dir, folder_name)
		# complete address of csv folder for chosen repo
	if not os.path.exists(csv_path):
		print("creating folder: " + csv_path)
		os.system("mkdir " + csv_path)
		process_log(repo, from_date, to_date, csv_path)

		if os.stat(os.path.join(
			csv_path, "logfile_" + repo + '_' + from_date + '_' + to_date + '.log')
		).st_size == 0:
			# if the generated logfile does not have data
			return False
	else:
		print("folder exists: " + csv_path)
	return True


# called by parse_csv
# checks is passed in string is in list of modules to be ignored
def ignore_module(entity):
	ignore_list = {'bower.json': ' ', '.gitignore': ' ', 'README.md': ' '}
		# list to be expanded
	if entity in ignore_list: return True
	else: return False


# called by result view
# reads opened csv file
# returns a list of the headers, and a dictionary of each row
def parse_csv(folder, filename):
	data_dict = [] # list of dictionaries, one dict for each row
	key_list = [] # list of row headers / keys

	try:
		csv_file = open(os.path.join(settings.csv_dir, folder, filename), 'rt')
	except (FileNotFoundError, IOError): 
		return ([], [])

	reader = csv.reader(csv_file)
	for i, row in enumerate(reader):
		temp_dict = {}
		if i == 0:
			# if first row of file, fill key_list with headers
			key_list = row
		else:
			if not row: break # if codemaat produces blank csv's
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

# called by get_word_frequency to handle adding / incrementing
# words to the frequency word_list
def parse_word(stem, word, word_list, stop_words):
	# skip adding if word is in stop_words
	if word in stop_words or len(word) == 1:
		return

	# add the word into the word_list
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
def get_word_frequency(folder, filename):
	try:
		logfile = open(os.path.join(settings.csv_dir, folder, filename), 'rt')
	except UnicodeError:
		logfile = io.open(os.path.join(settings.csv_dir, folder, filename), 
			'rt', encoding='utf-8')
	except (FileNotFoundError, IOError):
		return []
	log_list = logfile.read().split()

	word_list = []
	stemmer = LancasterStemmer()

	#define stop_words here rather than in a loop
	stop_words = get_stop_words('en')

	for word in log_list:
		# Strip, Stem, and then parse word into word_list
		word = word.strip("\"'/;:?{}[]!.,()").lower()
		stem = stemmer.stem(word)
		parse_word(stem,word,word_list,stop_words)

	# Sort and return selection of the word_list
	sorted_word_list = sorted(word_list, key = lambda x: x['freq'], reverse = True)

	textFreqPairs = []
	for word in sorted_word_list[:100]:
		key = max(word['text'].keys(), key=(lambda k: word['text'][k]))
		textFreqPairs.append({'text': key, 'freq': word['freq']})

	logfile.close()
	return (textFreqPairs, []) # blank array for keys variable

# retrieved from: http://stackoverflow.com/questions/3424899/
# 	+ whats-the-simplest-way-to-subtract-a-month-from-a-date-in-python
# def monthdelta(date, delta):
# 	m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
# 	if not m: m = 12
# 	d = min(date.day, [31,
# 		29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
# 	return date.replace(day=d,month=m, year=y)

# def get_prev_date():
# 	for m in range(-2, -1):
# 		month_string = str(monthdelta(datetime.now(), m))
# 	previous_date = ((month_string)[:10])

# 	return previous_date

# if __name__ == '__main__':
