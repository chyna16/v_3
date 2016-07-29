import requests
from requests.auth import HTTPBasicAuth
from json import load
import json
import codecs
import datetime
import settings


# called by: index view
# traverses api data and creates a list of project names
def get_projects():
	project_keys_list = []
	url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects?limit=100'

	try:
		projects = requests.get(url=url_projects,
			auth=(settings.username, settings.password))
		json_projects = json.loads(projects.text)
		for project in json_projects['values']:
			project_keys_list.append((project['key'],project['name']))
	except (requests.exceptions.ConnectionError, KeyError):
		print("api call failed")
	return project_keys_list


# called by: get_repo_url, repo_manager.refresh_repos
# returns requested value from specified repo's api data
def get_repo_detail(repo_name, category, value):
	repo_call = ('https://stash.mtvi.com/rest/api/1.0/repos?name=' + repo_name)
	try:
		repo_info = requests.get(url=repo_call,
			auth=(settings.username, settings.password))
		json_repo = json.loads(repo_info.text)

		data = json_repo['values'][0][category][value]
		return data
	except (requests.exceptions.ConnectionError, KeyError):
		return ''


# called by: _return_repos view
# makes new api call using selected project to get list of repos
def get_project_repos(selected_key, url_type, limit):
	url_repos = ('https://stash.mtvi.com/rest/api/1.0/projects/'
		+ selected_key
		+ '/repos?limit=' + limit)
	repo_list = []

	try:
		repos = requests.get(url=url_repos,
			auth=(settings.username, settings.password))
		json_repos = json.loads(repos.text)
		for repo_name in json_repos['values']:
			for link in repo_name['links']['clone']:
				if link['name'] == url_type:
					repo_list.append(
						{'name': repo_name['name'].replace(' ','-'), 'url': link['href']}
					)	# creates a list of dictionaries for every repo
	except (requests.exceptions.ConnectionError, KeyError):
		print("api call failed")
	return repo_list


# called by:
# 	_return_repo_dates view, repo_manager.refresh_repos/repo_check_and_update
# returns a list of datetimes of commits
def get_repo_timestamp(selected_key, selected_repo, limit):
	selected_repo = selected_repo
	url_repos = ('https://stash.mtvi.com/rest/api/1.0/projects/'
		+ selected_key + '/repos/' + selected_repo + '/commits?limit=' + limit)
	time_list = []
	converted_time_list = []

	try:
		repos = requests.get(url=url_repos,
			auth=(settings.username, settings.password))
		json_repos = json.loads(repos.text)
		for timestamp in json_repos['values']:
			time_list.append(timestamp['authorTimestamp'])
	except (requests.exceptions.ConnectionError, KeyError):
		print("api call failed")
	for timestamp in time_list:
		converted_time_list.append(
			str(datetime.datetime.fromtimestamp(timestamp/1000.0))
		)
	return converted_time_list


# called by: repo_manager.refresh_single_repo/repo_check_and_update
# makes api call to search for a repo by name and get clone url
def get_repo_url(repo_name, url_type):
	links = get_repo_detail(repo_name, 'links', 'clone')
	repo_url = ''
	try:
		for link in links:
			if link['name'] == url_type:
				repo_url = link['href']
	except KeyError:
		print("url not found")
	return repo_url


# if __name__ == '__main__':
