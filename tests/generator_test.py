import sys
sys.path.append('/home/farhat/Desktop/repos/v3.2')

from flask import Flask
import unittest
import os
import tempfile
from generator import parse_csv

class generatorTest(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		pass

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_parse_csv_function(self):
		with open('testfile.csv') as uploaded_file:
			dict_test, array_test = parse_csv(uploaded_file)

		self.assertEqual(dict_test, [{'stat': 'commits', 'value': '26'}, {'stat': 'entities', 'value': '24'}])
		self.assertEqual(array_test, ['stat', 'value'])


if __name__ == '__main__':
	unittest.main()