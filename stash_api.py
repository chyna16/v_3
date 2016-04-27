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
	global project_list
	project_list = []
	for projects in json_projects['values']:
		project_list.append(projects['name'])


def get_details():
	for project in json_projects['values']:
		print ("Project Name: " + project['name'])
		print ("Key: " + project['key'])
		if 'description' in project:
			print ("Description: " + project['description'])
		print ("-" * 60)


def get_clone_url():
	for project in json_projects['values']:
		project_key = project['key']
		url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + project_key + '/repos'

		repos = requests.get(url=url_repos, auth=('username', 'password'))

		json_repos = json.loads(repos.text)

		for repo in json_repos['values']:
			for link in repo['links']['clone']:
				if link['name'] == "http":
					print (link['href'])

get_project_names()

if __name__ == '__main__':
	get_project_names()
	print (project_list)
	get_details()