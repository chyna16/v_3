import requests
from requests.auth import HTTPBasicAuth
from json import load 
import json
import codecs
import settings # our script


url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects?limit=100' 
projects = requests.get(
	url=url_projects, auth=(settings.username, settings.password)
)	# retrieves data from api call using given username & password

# reader = codecs.getreader("utf-8")	
json_projects = json.loads(projects.text) 
	# converts retrieved data into a readable list of dictionaries


# called by visualizer
# traverses api data and creates a list of project names
def get_projects():
	project_keys_list = []
	for project in json_projects['values']:
		project_keys_list.append(project['key'])
	return project_keys_list


# CURRENTLY NOT IN USE
# traverses api data and reads details for each project
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


# called by index_repo view
# makes new api call using selected project to get list of repos
def get_project_repos(selected_key):
	url_repos = ('https://stash.mtvi.com/rest/api/1.0/projects/'
		+ selected_key 
		+ '/repos')
	repos = requests.get(
		url=url_repos, auth=(settings.username, settings.password)
	)
	json_repos = json.loads(repos.text)
	repo_list = []

	for repo_name in json_repos['values']:
		# traverses api data to find name and clone url for each repo
		for link in repo_name['links']['clone']:
			if link['name'] == "http":
				repo_list.append(
					{'name': repo_name['name'], 'url': link['href']}
				)	# creates a list of dictionaries for every repo
	return repo_list

if __name__ == '__main__':
	get_projects()

