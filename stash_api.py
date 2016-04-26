import requests
from requests.auth import HTTPBasicAuth
from json import load 
import json
import codecs

url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects' 
projects = requests.get(url=url_projects, auth=('username', 'password'))

# reader = codecs.getreader("utf-8")
json_projects = json.loads(projects.text)

for project in json_projects['values']:
	project_key = project['key']
	url_repos = 'https://stash.mtvi.com/rest/api/1.0/projects/' + project_key + '/repos'

	repos = requests.get(url=url_repos, auth=('username', 'password'))

	json_repos = json.loads(repos.text)

	for repo in json_repos['values']:
		for link in repo['links']['clone']:
			if link['name'] == "http":
				print (link['href'])
