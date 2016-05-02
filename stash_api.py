import requests
from requests.auth import HTTPBasicAuth
from json import load 
import json
import codecs


url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects' 
projects = requests.get(url=url_projects, auth=('username', 'password'))

# reader = codecs.getreader("utf-8")	
json_projects = json.loads(projects.text)

# print(projects)

# def get_project_url():
# 	for project in json_projects['values']:
# 		for details in project['links']['self']:
# 			print (details['href'])


def get_project_names():
	# global project_list
	project_list = []
	for projects in json_projects['values']:
		project_list.append(projects['name'])


def get_project_keys():
	project_keys_list = []
	for project in json_projects['values']:
		project_keys_list.append(project['key'])

	return project_keys_list


def get_details():
	# global project_key
	# global project_name
	# global project_description
	for project in json_projects['values']:
		project_key = project['key']
		project_name = project['name']
		print ("Project Name: " + project_name)
		print ("Key: " + project_key)
		if 'description' in project:
			project_description = project['description']
			print ("Description: " + project_description)
		print ("-" * 60)

# def get_repo_list():
# 	for projects in json_projects['values']:
# 	project_key.append(projects['key'])


# def get_clone_url():
# 	for project in json_projects['values']:
# 		project_key = project['key']
# 		url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + project_key + '/repos'

# 		repos = requests.get(url=url_repos, auth=('username', 'password'))

# 		json_repos = json.loads(repos.text)

# 		for repo in json_repos['values']:
# 			for link in repo['links']['clone']:
# 				if link['name'] == "http":
# 					print (link['href'])

def get_project_repo_name(selected_key):
	project_repo_name
	# for project in json_projects['values']:
		# project_key = project['key']
	url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + selected_key + '/repos'

	repos = requests.get(url=url_repos, auth=('username', 'password'))

	project_repo_name = []
	json_repos = json.loads(repos.text)	
	for repo_names in json_repos['values']:
		project_repo_name.append(repo_names['name'])

	return project_repo_name

def get_project_repo_url(selected_key):
	# global repo_list
	# global url_repos
	# for project in json_projects['values']:
		# project_key = project['key']
	url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + selected_key + '/repos'

	repos = requests.get(url=url_repos, auth=('username', 'password'))

	repo_list = []
	json_repos = json.loads(repos.text)
	for repo in json_repos['values']:
		for link in repo['links']['clone']:
			if link['name'] == "http":
				repo_list.append(link['href'])

	return repo_list

# get_details()
# get_project_names()
# get_project_key()

if __name__ == '__main__':
	# get_project_names()
	# print (project_list)
	get_details()
	# get_clone_url()
	# get_project_repo_url(selected_key= "ARC")
	# print("-" * 80)
	# print(repo_list)
	# get_project_repo_name(selected_key= "ARC")
	# # print(url_repos)
	# print("-" * 80)
	# print(project_repo_name)
