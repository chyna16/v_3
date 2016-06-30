import settings
import sys
sys.path.append(settings.v3_dir)
import os
import csv
from flask import Flask
import unittest
import tempfile
import shutil
from nltk.stem.lancaster import LancasterStemmer
from stop_words import get_stop_words
import generator


class generatorTest(unittest.TestCase):
	def setUp(self):
		self.stemmer = LancasterStemmer()
		
		self.temp_dir = tempfile.mkdtemp()

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

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)


	def test_parse_csv_output(self):
		with open('testfile.csv') as uploaded_file:
			dict_test, array_test = generator.parse_csv(uploaded_file)

		self.assertEqual(dict_test, 
			[{'stat': 'commits', 'value': '26'}, {'stat': 'entities', 'value': '24'}]
		)
		self.assertEqual(array_test, ['stat', 'value'])

	def test_get_lines_list_output(self):
		result = generator.get_lines_list('test')
		self.assertEqual(result, [{'entity': 'test.py', 'lines': '10'}])

	def test_get_merge_list_output(self):
		result = generator.get_lines_list('test')
		new_result = generator.get_merge_list('test', result)
		self.assertEqual(new_result, [{'entity': 'test.py', 'n-revs': '8', 'lines': '10'}])

	def test_merge_csv_error(self):
		generator.merge_csv('sdndks')
		self.assertRaises(IOError)
	
	def test_merge_csv_success(self):
		generator.merge_csv('test')
		assert os.path.exists(os.path.join(self.temp_dir, 'hotspots_test.csv'))

	def test_merge_csv_correctness(self):
		generator.merge_csv('test')
		with open('hotspots_test.csv') as hotspots:
			reader = csv.DictReader(hotspots)

			self.assertEqual(reader.fieldnames, ['entity', 'n-revs', 'lines'])
			for row in reader:
				self.assertEqual(row['entity'], 'test.py')
				self.assertEqual(row['n-revs'], '8')
				self.assertEqual(row['lines'], '10')

	def test_get_word_frequency_output(self):
		with open('wordtest.log') as logfile:
			words = generator.get_word_frequency(logfile)

			self.assertEqual(words, [
				{'text': 'word', 'freq': 2, 'stem': 'word'},
				{'text': 'one', 'freq': 1, 'stem': 'on'},
				{'text': 'two', 'freq': 1, 'stem': 'two'}
			])

	def test_word_exists_bool(self):
		word_list = [{'text': 'one', 'freq': 1, 'stem': 'on'}]
		
		self.assertTrue(generator.word_exists(
			self.stemmer.stem('one'), 'one', word_list))

	def test_word_exists_result(self):
		word_list = [
			{'text': 'added', 'freq': 1, 'stem': self.stemmer.stem('added')}
		]

		generator.word_exists(self.stemmer.stem('add'), 'add', word_list)
		self.assertEqual(len(word_list), 1)
		self.assertEqual(word_list[0]['freq'], 2)
		self.assertEqual(word_list[0]['text'], 'add')

	def test_redundant_word_bool(self):
		stop_words = get_stop_words('en')
		self.assertTrue(generator.redundant_word('and'))
		self.assertTrue(generator.redundant_word('3'))
		self.assertTrue(generator.redundant_word('&'))
		self.assertFalse(generator.redundant_word('make'))
		self.assertFalse(generator.redundant_word('implement'))
		self.assertFalse(generator.redundant_word('remove'))

	def test_ignore_module_false(self):
		result = generator.ignore_module("test")
		self.assertFalse(result)

	def test_ignore_module_true(self):
		result = generator.ignore_module(".gitignore")
		self.assertTrue(result)

	def test_create_log(self):
		generator.create_log('v3_test', '', '', settings.v3_dir + '/.git')
		assert os.path.isfile('logfile_v3_test__.log')

	def test_run_codemaat(self):
		generator.set_path(settings.maat_dir)
		generator.create_log('v3_test', '', '', settings.v3_dir + '/.git')
		generator.run_codemaat('summary', 'summary_test', 'v3', '', '')
		assert os.path.isfile('summary_test_v3.csv')

	# def test_generate_summary(self):
	# 	generator.generate_data_summary('v3_test', '', '')
	# 	assert os.path.exists('summary_v3_test.csv')

	# def test_generate_coupling(self):
	# 	generator.generate_data_coupling('v3_test', '', '')
	# 	assert os.path.exists('coupling_v3_test.csv')

	# def test_generate_metrics(self):
	# 	generator.generate_data_metrics('v3_test', '', '')
	# 	assert os.path.exists('metrics_v3_test.csv')



if __name__ == '__main__':
	unittest.main()