import sys
sys.path.append('..')
import settings
import stash_api
import requests
from requests.auth import HTTPBasicAuth
from json import load
import json
import codecs
import datetime
import unittest


class ApiCallTests(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		pass

	@classmethod
	def tearDownClass(self):
		pass

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_get_repo_url_http(self):
		url = stash_api.get_repo_url('arc-ui', 'http')
		self.assertIn('arc-ui.git', url)
		self.assertIn('http', url)

	def test_get_repo_url_ssh(self):
		url = stash_api.get_repo_url('arc-ui', 'ssh')
		self.assertIn('arc-ui.git', url)
		self.assertIn('ssh', url)

	def test_get_repo_timestamp_date(self):
		timestamp = stash_api.get_repo_timestamp('bot', 'mcshake', '1')[0].split(' ')
		self.assertIs(2, len(timestamp))
		date = timestamp[0].split('-')
		self.assertIs(3, len(date))

	def test_get_repo_timestamp_time(self):
		timestamp = stash_api.get_repo_timestamp('bot', 'mcshake', '1')[0].split(' ')
		self.assertIs(2, len(timestamp))
		time = timestamp[1].split(':')
		self.assertIs(3, len(time))

	def test_get_project_repos(self):
		repos = stash_api.get_project_repos('BOT', 'http', '100')
		self.assertIn('stash.mtvi.com/scm/bot', repos[0]['url'])

	def test_get_repo_detail(self):
		key = stash_api.get_repo_detail('arc-ui', 'project', 'key')
		self.assertEqual('ARC', key)

	def test_get_projects(self):
		projects = stash_api.get_projects()
		self.assertIn(('AO', 'Always On'), projects)


if __name__ == '__main__':
	unittest.main()