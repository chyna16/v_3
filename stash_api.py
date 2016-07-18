import requests
from requests.auth import HTTPBasicAuth
from json import load
import json
import codecs
import datetime
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
	try:
		for project in json_projects['values']:
			project_keys_list.append((project['key'],project['name']))
	except KeyError:
		print("api call failed")
	return project_keys_list


# CURRENTLY NOT IN USE
# traverses api data and reads details for each project
def get_details():
	try:
		for project in json_projects['values']:
			project_key = project['key']
			project_name = project['name']
			print ("Project Name: " + project_name)
			print ("Key: " + project_key)
			if 'description' in project:
				project_description = project['description']
				print ("Description: " + project_description)
			print ("-" * 60)
	except KeyError:
		print("api call failed")


# called by index_repo view
# makes new api call using selected project to get list of repos
def get_project_repos(selected_key, url_type):
	url_repos = ('https://stash.mtvi.com/rest/api/1.0/projects/'
		+ selected_key
		+ '/repos')
	repos = requests.get(
		url=url_repos, auth=(settings.username, settings.password)
	)
	json_repos = json.loads(repos.text)
	repo_list = []

	try:
		for repo_name in json_repos['values']:
			# traverses api data to find name and clone url for each repo
			for link in repo_name['links']['clone']:
				if link['name'] == url_type:
					repo_list.append(
						{'name': repo_name['name'], 'url': link['href']}
					)	# creates a list of dictionaries for every repo
	except KeyError:
		print("api call failed")

	return repo_list

def get_repo_timestamp(selected_key, selected_repo, url_type, limit):
	selected_repo = selected_repo.replace(' ','-')
	url_repos = ('https://stash.mtvi.com/rest/api/1.0/projects/'
		+ selected_key + '/repos/' + selected_repo + '/commits?limit='+limit)
	repos = requests.get(
		url=url_repos, auth=(settings.username, settings.password)
	)
	json_repos = json.loads(repos.text)
	time_list = []
	converted_time_list = []

	try:
		for timestamp in json_repos['values']:
					time_list.append(
						timestamp['authorTimestamp']
					)	# creates a list of dictionaries for every repo
	except KeyError:
		print("api call failed")
	for timestamp in time_list:
		converted_time_list.append(str(datetime.datetime.fromtimestamp
			(timestamp/1000.0)))

	return converted_time_list

# called by clone_repos in generator
# makes api call to search for a repo by name
def get_repo_url(repo_name, url_type):
	repo_call = ('https://stash.mtvi.com/rest/api/1.0/repos?name=' + repo_name)
	repo_info = requests.get(
		url=repo_call, auth=(settings.username, settings.password)
	)
	json_repo = json.loads(repo_info.text)

	if json_repo['size'] == 0: return False

	try:
		for link in json_repo['values'][0]['links']['clone']:
			if link['name'] == url_type:
				repo_url = link['href']
	except KeyError:
		print("api call failed")

	return repo_url


# if __name__ == '__main__':
