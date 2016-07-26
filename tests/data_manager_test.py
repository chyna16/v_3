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
import data_manager


class DataManagerTests(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.temp_dir = tempfile.mkdtemp()

		self.stemmer = LancasterStemmer()

		l = open(os.path.join(self.temp_dir, 'lines_test.csv'), 'w')
		l.writelines(['language,filename,blank,comment,code,' +
			'"http://cloc.sourceforge.net v 1.60  T=0.22 s (49.4 files/s, 1908.9 lines/s)"\n',
			'Python,test.py,5,5,10'])
		l.close()

		m = open(os.path.join(self.temp_dir, 'metrics_test.csv'), 'w')
		m.writelines(['entity,n-authors,n-revs\n', 'test.py,1,8'])
		m.close()

		s = open(os.path.join(self.temp_dir, 'testfile.csv'), 'w')
		s.writelines(['stat,value\n', 'commits,26\n', 'entities,24'])
		s.close()

		w = open(os.path.join(self.temp_dir, 'wordtest.log'), 'w')
		w.writelines(['word one\n', 'word two'])
		w.close()

		os.chdir(self.temp_dir)

	@classmethod
	def tearDownClass(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)

	def setUp(self):
		pass

	def tearDown(self):
		pass


	def test_parse_csv_output(self):
		dict_test, array_test = data_manager.parse_csv(self.temp_dir, 'testfile.csv')

		self.assertEqual(dict_test,
			[{'stat': 'commits', 'value': '26'}, {'stat': 'entities', 'value': '24'}]
		)
		self.assertEqual(array_test, ['stat', 'value'])

	def test_get_lines_list_output(self):
		result = data_manager.get_lines_list('test')
		self.assertEqual(result, [{'entity': 'test.py', 'lines': '10'}])

	def test_get_merge_list_output(self):
		result = data_manager.get_lines_list('test')
		new_result = data_manager.get_merge_list('test', result)
		self.assertEqual(new_result, [{'entity': 'test.py', 'n-revs': '8', 'lines': '10'}])

	def test_merge_csv_error(self):
		data_manager.merge_csv('sdndks')
		self.assertRaises(IOError)

	def test_merge_csv_success(self):
		data_manager.merge_csv('test')
		assert os.path.exists(os.path.join(self.temp_dir, 'hotspots_test.csv'))

	def test_merge_csv_correctness(self):
		data_manager.merge_csv('test')
		with open('hotspots_test.csv') as hotspots:
			reader = csv.DictReader(hotspots)

			self.assertEqual(reader.fieldnames, ['entity', 'n-revs', 'lines'])
			for row in reader:
				self.assertEqual(row['entity'], 'test.py')
				self.assertEqual(row['n-revs'], '8')
				self.assertEqual(row['lines'], '10')

	def test_get_word_frequency_output(self):
		words, keys = data_manager.get_word_frequency(self.temp_dir, 'wordtest.log')

		self.assertEqual(words, [
			{'text': 'word', 'freq': 2},
			{'text': 'one', 'freq': 1},
			{'text': 'two', 'freq': 1}
		])

	def test_ignore_module_false(self):
		result = data_manager.ignore_module("test")
		self.assertFalse(result)

	def test_ignore_module_true(self):
		result = data_manager.ignore_module(".gitignore")
		self.assertTrue(result)


if __name__ == '__main__':
	unittest.main()