import sys
sys.path.append('..')
import settings
import os
import csv
from flask import Flask
import unittest
import tempfile
import shutil
from nltk.stem.lancaster import LancasterStemmer
from stop_words import get_stop_words
import generator


class ApiCallTests(unittest.TestCase):
	def setUp(self):
		pass
		# self.url_projects = 'https://stash.mtvi.com/rest/api/1.0/projects?limit=100'
		# self.projects = requests.get(
		# 	url=url_projects, auth=(settings.username, settings.password)
		# )	# retrieves data from api call using given username & password

		# # reader = codecs.getreader("utf-8")
		# self.json_projects = json.loads(projects.text)
		# 	# converts retrieved data into a readable list of dictionaries

	def tearDown(self):
		pass