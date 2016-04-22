import sys
import os
import settings
sys.path.append(settings.t_test_dir)

from flask import Flask
import unittest
import tempfile
import generator
from generator import generate_data
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
	
	def test_generate_data(self):
		self.assertEqual(generate_data(generator.date_after), generate_data(generator.date_before))
		self.assertNotEqual(("12-02-1993"), generate_data(generator.date_before))
		self.assertNotEqual((generate_data(generator.date_after)), ("04-21-2016"))
		self.assertNotEqual(("01-30-2014"), ("04-21-2016"))

	def test_csv_folder_exists(self):
		assert os.path.exists("csv_files___")



if __name__ == '__main__':
	unittest.main()