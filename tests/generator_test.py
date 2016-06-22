import sys
import os
import settings
sys.path.append(settings.test_dir)
import csv
from flask import Flask
import unittest
import tempfile
import generator


class generatorTest(unittest.TestCase):
	def setUp(self):
		generator.merge_csv('test')

	def tearDown(self):
		pass

	def test_parse_csv_output(self):
		with open('testfile.csv') as uploaded_file:
			dict_test, array_test = generator.parse_csv(uploaded_file)

		self.assertEqual(dict_test, 
			[{'stat': 'commits', 'value': '26'}, {'stat': 'entities', 'value': '24'}]
		)
		self.assertEqual(array_test, ['stat', 'value'])

	def test_merge_csv_error(self):
		generator.merge_csv('sdndks')
		self.assertRaises(IOError)
	
	def test_merge_csv_result(self):
		assert os.path.exists('hotspots_test.csv')

	def test_merge_csv_correctness(self):
		with open('hotspots_test.csv') as hotspots:
			reader = csv.DictReader(hotspots)

			self.assertEqual(reader.fieldnames, ['entity', 'n-revs', 'lines'])
			for row in reader:
				self.assertEqual(row['entity'], 'test.py')
				self.assertEqual(row['n-revs'], '8')
				self.assertEqual(row['lines'], '10')

	def test_word_frequency_output(self):
		with open('word_test.log') as logfile:
			words = generator.get_word_frequency(logfile)

			self.assertEqual(words, [
				{'text': 'word', 'size': 2},
				{'text': 'one', 'size': 1},
				{'text': 'two', 'size': 1}
			])

	def test_ignore_module_false(self):
		result = generator.ignore_module("test")
		self.assertFalse(result)

	def test_ignore_module_true(self):
		result = generator.ignore_module(".gitignore")
		self.assertTrue(result)






	# def test_generate_data(self):
	# 	self.assertEqual(generate_data(generator.date_after), generate_data(generator.date_before))
	# 	self.assertNotEqual(("12-02-1993"), generate_data(generator.date_before))
	# 	self.assertNotEqual((generate_data(generator.date_after)), ("04-21-2016"))
	# 	self.assertNotEqual(("01-30-2014"), ("04-21-2016"))

	# def test_csv_folder_exists(self):
	# 	assert os.path.exists("csv_files___")



if __name__ == '__main__':
	unittest.main()