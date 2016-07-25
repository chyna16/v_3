import sys
sys.path.append('..')
import unittest
import os
import fnmatch
import json
import io
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import generator # our script
import data_manager # our script
import repo_manager
import stash_api # our script
import settings # our script
from apscheduler.schedulers.background import BackgroundScheduler
from flask.ext.cache import Cache
import flask
from flask_testing import LiveServerTestCase, TestCase
import visualizer


class ViewTests(unittest.TestCase):
	def setUp(self):
		self.app = visualizer.app.test_client()
		self.app.testing = True

		if not os.path.exists(os.path.join(settings.repo_dir, 'mcshake')):
			url = stash_api.get_repo_url('mcshake', 'http')
			repo_manager.clone_repo(url, settings.repo_dir, settings.password)
			generator.manage_csv_folder('mcshake', '2014-10-24', '2014-12-23')

	def tearDown(self):
		pass

	def test_index_status_code(self):
		result = self.app.get('/')
		self.assertEqual(result.status_code, 200)

	def test_dashboard_status_code(self):
		result = self.app.get('/dashboard')
		self.assertEqual(result.status_code, 200)

	def test_result_status_code(self):
		result = self.app.get('/result')
		self.assertEqual(result.status_code, 200)

	def test_dashboard_content(self):
		response = self.app.get('/result?repo_name=mcshake' 
			+ '&analysis=metrics&from_date=2014-10-24&to_date=2014-12-23')
		self.assertEqual(response.status_code, 200)
		self.assertIn('<button class="btn btn-link" type="submit" ' 
			+ 'name="analysis" value="metrics">Metrics</button>', 
			str(response.data))

	def test_result_content(self):
		response = self.app.get('/result?repo_name=mcshake' 
			+ '&analysis=metrics&from_date=2014-10-24&to_date=2014-12-23')
		self.assertEqual(response.status_code, 200)
		self.assertIn('var keys = ["entity", "n-authors", "n-revs"]', 
			str(response.data))

	def test_result_invalid(self):
		response = self.app.get('/result?repo_name=djnal' 
			+ '&analysis=metrics&from_date=2014-10-24&to_date=2014-12-23')
		self.assertEqual(response.status_code, 200)
		self.assertIn('Not found', 
			str(response.data))

	def test_result_query(self):
		app = flask.Flask(__name__)
		with app.test_request_context('/result?repo_name=mcshake' 
			+ '&analysis=metrics&from_date=2014-10-24&to_date=2014-12-23'):
			assert flask.request.path == '/result'
			assert flask.request.args['analysis'] == 'metrics'

	def test_return_repos(self):
		response = self.app.get('/_return_repos?key=bot')
		self.assertEqual(response.status_code, 200)
		self.assertIn('MCShake', str(response.data))

	def test_return_repo_dates(self):
		response = self.app.get('/_return_repo_dates?key=bot&name=mcshake')
		self.assertEqual(response.status_code, 200)
		self.assertIn('2014-10-24 12:41:19', str(response.data))



if __name__ == '__main__':
	unittest.main()