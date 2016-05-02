import requests
from requests.auth import HTTPBasicAuth
from json import load 
import json
import codecs


url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects' 
projects = requests.get(url=url_projects, auth=('username', 'password'))

# reader = codecs.getreader("utf-8")	
json_projects = json.loads(projects.text)


def get_project_names():
	project_list = []
	for projects in json_projects['values']:
		project_list.append(projects['name'])


def get_project_keys():
	project_keys_list = []
	for project in json_projects['values']:
		project_keys_list.append(project['key'])

	return project_keys_list


def get_details():
	for project in json_projects['values']:
		project_key = project['key']
		project_name = project['name']
		print ("Project Name: " + project_name)
		print ("Key: " + project_key)
		if 'description' in project:
			project_description = project['description']
			print ("Description: " + project_description)
		print ("-" * 60)


def get_project_repo_name(selected_key):
	url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + selected_key + '/repos'

	repos = requests.get(url=url_repos, auth=('username', 'password'))

	project_repo_names = []
	json_repos = json.loads(repos.text)	
	for repo_names in json_repos['values']:
		project_repo_names.append(repo_names['name'])

	return project_repo_names


def get_project_repo_url(selected_key):
	url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + selected_key + '/repos'

	repos = requests.get(url=url_repos, auth=('username', 'password'))

	project_repo_urls = []
	json_repos = json.loads(repos.text)
	for repo in json_repos['values']:
		for link in repo['links']['clone']:
			if link['name'] == "http":
				project_repo_urls.append(link['href'])

	return project_repo_urls


# if __name__ == '__main__':
