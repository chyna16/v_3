import csv, os, time

# currently the codemaat directory is hardcoded
if os.name == 'nt':
	# root_dir = os.path.normpath(owd + '/csv_files_' + repo_name)
	maat_dir = ('C:\\Users\\bentinct\\winmaat0.8.5\\')
	# repo_dir = ('C:\\Users\\bentinct\\repos\\mcshake\\.git')
	repo_list = ('C:\\Users\\bentinct\\repos\\')
	# repo_name = os.path.basename(os.path.normpath(repo_dir))
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]
else:
	# root_dir = owd + '/csv_files_' + repo_name
	maat_dir = '/home/tramain/ixmaat0.8.5'
	# maat_dir = '/home/farhat/ixmaat0.8.5'
	# repo_dir = '/home/tramain/mcshake/.git'
	# repo_dir = '/home/farhat/Desktop/repos/mcshake/.git'
	repo_list = '/home/tramain/repos/'
	folder_list = [ item for item in os.listdir(repo_list) if os.path.isdir(os.path.join(repo_list, item)) ]

# repo_name gets used once the flask script is run
repo_name = ""
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
	# creates folder for the root_dir variable if none exists
	os.system("mkdir csv_files_" + repo_name)
	os.chdir("csv_files_" + repo_name)


def generate_data(address):
	print("Obtaining repository logs...")
	# currently manually selects the repository
	os.system('git --git-dir ' + address + ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat > logfile_' + repo_name + '.log')
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
	print("Creating coupling summary...")
	os.system("maat -l logfile_" + repo_name + ".log -c git -a coupling > coupling_" + repo_name + ".csv")
	# Reports correlation of files that often commit together
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
			row_array.append(row)
	for i, key in enumerate(key_array):
		col_array = []
		for r in row_array:
			col_array.append(r[i])
		data_dict[key] = col_array
	return (data_dict, key_array)