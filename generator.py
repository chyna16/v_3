import csv, os, time, fnmatch

if os.name == 'nt':
	maat_dir = ('C:\\Users\\bentinct\\winmaat0.8.5\\')
	repo_list = ('C:\\Users\\bentinct\\repos\\')
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]
else:
	maat_dir = '/home/tramain/ixmaat0.8.5'
	# maat_dir = '/home/farhat/ixmaat0.8.5'
	repo_list = '/home/tramain/repos/'
	# repo_list = '/home/farhat/Desktop/repos/'
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]

# repo_name is used for later functions once a repository is selected from the home page
repo_name = ""
# once a date is selected on the home page, this variable is used
date_after = ""
# this returns only files of this type to the dashboard function to display.
file_type = '*.csv'

def set_path(repo_name):
	print("Setting a path for codemaat...")
	# path is set temporarily, per script run
	os.environ['PATH'] += os.pathsep + maat_dir
	print("Done.")
	print("-" * 60)
	# need to create an exception if csv_files folder already exists
	# global owd
	# owd = os.getcwd()


def generate_data(address):
	# creates folder for the root_dir variable if none exists
	os.system("mkdir csv_files_" + repo_name)
	os.chdir("csv_files_" + repo_name)
	print("Obtaining repository logs...")
	if date_after == "":
		os.system('git --git-dir ' + address + ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat > logfile_' + repo_name + '.log')
	else:
		os.system('git --git-dir ' + address + ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat --after=' + date_after + ' > logfile_' + repo_name + '_' + date_after + '.log')
	print("Done.")
	print("-" * 60)
	print("Creating csv files from generated log...")
	time.sleep(1)
	print("Creating repository summary...")
	# currently running codemaat via 'maat.bat' on windows creates extra lines of code in the csv files,
	# causing them to break when requested from the site
	os.system("maat -l logfile_" + repo_name + ".log -c git -a summary > summary_" + repo_name + ".csv")
	# Reports an overview of mined data from git's log file
	print("Creating organizational metrics summary...")
	os.system("maat -l logfile_" + repo_name + ".log -c git > metrics_" + repo_name + ".csv")
	# Reports the number of authors/revisions made per module
	# print("Creating coupling summary...")
	# os.system("maat -l logfile_" + repo_name + ".log -c git -a coupling > coupling_" + repo_name + ".csv")
	# Reports correlation of files that often commit together, currently broken
	# degree = % of commits where the two files were changed in the same commit
	print("Creating code age summary...")
	os.system("maat -l logfile_" + repo_name + ".log -c git -a entity-churn > age_" + repo_name + ".csv")
	# Reports how long ago the last change was made in measurement of months
	print("Done. Check your current folder for your files.")
	print("-" * 60)
	os.chdir("..")


# this function takes csv file and two empty arrays
# reads each column from file into an array and returns the arrays
def parse_csv(uploaded_file):
	reader = csv.reader(uploaded_file)
	data_dict = {}
	key_array = []
	row_array = []
	for i, row in enumerate(reader):
		if i == 0:
			key_array = row
		else:
			# temporary feature to narrow crabapple's age analysis
			if 'age_crabapple' in str(uploaded_file): 
				if row[2] != '0':
					row_array.append(row)
			else:
				row_array.append(row)
	for i, key in enumerate(key_array):
		col_array = []
		for r in row_array:
			col_array.append(r[i])
		data_dict[key] = col_array
	return (data_dict, key_array)


# functions below remove the garbage lines added to the csv files on windows
def skip_lines(file, lines):
	for i, rows in enumerate(file):
		if i >= lines:
			yield rows


def win_csv(root_dir, csv_name):
	junk_file = open(root_dir + "/" + csv_name, 'rt')
	reader = csv.reader(junk_file)
	row1 = next(reader)
	if row1 == []:
		clean_file = open(root_dir + '\\_' + csv_name, 'wt', newline = '')
		write = csv.writer(clean_file, csv.QUOTE_ALL)
		for row in skip_lines(reader, 3):
			write.writerow(row)
	else:
		return False
