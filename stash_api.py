import requests
from requests.auth import HTTPBasicAuth
from json import load 
import json
import codecs


url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects' 
projects = requests.get(url=url_projects, auth=('username', 'password'))

# reader = codecs.getreader("utf-8")	
json_projects = json.loads(projects.text)


def get_projects():
	# project_names_list = []
	project_keys_list = []
	for project in json_projects['values']:
		# project_names_list.append(project['name'])
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


def get_project_repos(selected_key):
	url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + selected_key + '/repos'

	repos = requests.get(url=url_repos, auth=('username', 'password'))

	repos_dict = []

	json_repos = json.loads(repos.text)	
	for repo_name in json_repos['values']:
		# project_repo_names.append(repo_name['name'])
		for link in repo_name['links']['clone']:
			if link['name'] == "http":
				# project_repo_urls.append(link['href'])
				repos_dict.append({'name': repo_name['name'], 'url': link['href']})

	return (repos_dict)


if __name__ == '__main__':
	get_project_repos('ARC')

