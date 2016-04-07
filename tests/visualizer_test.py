import sys
sys.path.append('/home/farhat/Desktop/repos/v3.2')

from flask import Flask
import unittest
import os
import tempfile
import visualizer


class SampleTests(unittest.TestCase):

	# @classmethod
	# def setUpClass(cls):
	# 	pass

	# @classmethod
	# def tearDownClass(cls):
	# 	pass

	def setUp(self):
		self.app = visualizer.app.test_client()
		self.app.testing = True

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


if __name__ == '__main__':
	unittest.main()