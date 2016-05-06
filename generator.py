import csv
import os
import time
import fnmatch
import subprocess


def set_path(maat_dir):
	print("Setting a path for codemaat...")
	# path is set temporarily, per script run
	os.environ['PATH'] += os.pathsep + maat_dir
	print("Done.")
	print("-" * 60)


def create_log(repo_name, date_after, date_before, address):
	sys_command = "" # resets to blank

	# first part of command same for any date specification
	sys_command = 'git --git-dir ' + address + ' log --pretty=format:"[%h] %aN %ad %s" --date=short --numstat'
	#the following commands change depending on date specification
	if not date_after == "" and date_before == "":
		print("date after selected")
		sys_command += ' --after=' + date_after 	
	elif date_after == "" and not date_before == "":
		print("date before selected")
		sys_command += ' --before=' + date_before 	
	elif not date_after == "" and not date_before == "":
		print("date_after and date_before selected")
		sys_command += ' --after=' + date_after + ' --before=' + date_before 	
	# last part of command same for any date specification			
	sys_command += ' > logfile_' + repo_name + '_' + date_after + '_' + date_before + '.log'

	os.system(sys_command) # command line call using the updated string


def generate_data(address, repo_name, date_after, date_before):
	# creates folder for the root_dir variable if none exists
	os.system("mkdir csv_files_" + repo_name + "_" + date_after + "_" + date_before)
	os.chdir("csv_files_" + repo_name + "_" + date_after + "_" + date_before)
	print("Obtaining repository logs...")
	create_log(repo_name, date_after, date_before, address)
	print("Done.")
	print("-" * 60)
	print("Creating csv files from generated log...")
	time.sleep(1)
	print("Creating repository summary...")
	# print("maat -l logfile_" + repo_name + "_" + date_after + "_" 
	# 	+ date_before + ".log -c git -a summary > summary_" + repo_name 
	# 	+ ".csv")
	os.system("maat -l logfile_" + repo_name + "_" + date_after + "_" 
		+ date_before + ".log -c git -a summary > summary_" + repo_name 
		+ ".csv")
	# # Reports an overview of mined data from git's log file
	# print("Creating organizational metrics summary...")
	# os.system("maat -l logfile_" + repo_name + "_" + date_after + "_" 
	# 	+ date_before + ".log -c git > metrics_" + repo_name + ".csv")
	# # Reports the number of authors/revisions made per module
	# print("Creating coupling summary...")
	# os.system("maat -l logfile_" + repo_name + "_" + date_after + "_" 
	# 	+ date_before + ".log -c git -a coupling > coupling_" + repo_name 
	# 	+ ".csv")
	# # Reports correlation of files that often commit together
	# # degree = % of commits where the two files were changed in the same commit
	# print("Creating code age summary...")
	# os.system("maat -l logfile_" + repo_name + "_" + date_after + "_" 
	# 	+ date_before + ".log -c git -a entity-churn > age_" + repo_name 
	# 	+ ".csv")
	# Reports how long ago the last change was made in measurement of months
	print("Done. Check your current folder for your files.")
	print("-" * 60)
	os.chdir("..")


def submit_url(clone_url, password):
	char = clone_url.index('@')
	os.chdir('..')
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
	return message
	os.chdir('v3')

# this function takes csv file and two empty arrays
# reads each column from file into an array and returns the arrays
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


if __name__ == '__main__':
	# print (folder_list)
	# print (project_list)
	print(project_key)
