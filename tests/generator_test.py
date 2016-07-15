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
from datetime import datetime
import generator


class FileParserTests(unittest.TestCase):
	def setUp(self):
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
				{'text': 'word', 'freq': 2},
				{'text': 'one', 'freq': 1},
				{'text': 'two', 'freq': 1}
			])

	def test_ignore_module_false(self):
		result = generator.ignore_module("test")
		self.assertFalse(result)

	def test_ignore_module_true(self):
		result = generator.ignore_module(".gitignore")
		self.assertTrue(result)


class FileManagingTests(unittest.TestCase):
	def setUp(self):
		self.temp_dir = tempfile.mkdtemp()
		os.chdir(self.temp_dir)

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)


	def test_create_log(self):
		generator.create_log('logfile', 'v3_test', '', '', settings.v3_dir + '/.git')
		assert os.path.isfile('logfile_v3_test__.log')

	def test_run_codemaat(self):
		generator.set_path(settings.maat_dir)
		generator.create_log('logfile', 'v3_test', '', '', settings.v3_dir + '/.git')
		generator.run_codemaat('summary', 'summary_test', 'v3', '', '')
		assert os.path.isfile('summary_test_v3.csv')


class RepoManagingTests(unittest.TestCase):
	def setUp(self):
		self.temp_dir = tempfile.mkdtemp()
		generator.repo_dir = self.temp_dir
		os.chdir(self.temp_dir)

		self.repo_url = 'https://'+settings.username+'@stash.mtvi.com/scm/bot/mcshake.git'

		# sample_repo_url = stash_api.get_repo_url('mcshake', 'http')
		# generator.clone_repo(self.repo_url, os.pathself.temp_dir, settings.password)

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)


	def test_get_dir_list(self):
		os.system("mkdir test_dir_1")
		os.system("mkdir test_dir_2")
		dir_list = generator.get_dir_list(self.temp_dir)
		self.assertIn('test_dir_1', dir_list)
		self.assertIn('test_dir_2', dir_list)
		shutil.rmtree('test_dir_1')
		shutil.rmtree('test_dir_2')

	def test_clone_repo(self):
		generator.clone_repo(self.repo_url, self.temp_dir, settings.password)
		assert os.path.isdir('mcshake')
		shutil.rmtree('mcshake')

	def test_clone_command(self):
		clone_cmd = generator.get_clone_command('https://test_name@stash.mtvi.com', 'qwerty')
		self.assertEqual(clone_cmd, 'https://test_name:qwerty@stash.mtvi.com')

	def test_add_datetime(self):
		generator.add_datetime(self.temp_dir)
		assert os.path.isfile('timetag.txt')
		os.remove('timetag.txt')

	def test_get_commit_dates(self):
		if not os.path.isdir('mcshake'):
			generator.clone_repo(self.repo_url, self.temp_dir, settings.password)
		f_date, l_date = generator.get_commit_dates('mcshake')
		date_length = len(f_date.split('-'))
		self.assertEqual(date_length, 3)
		shutil.rmtree('mcshake')

	def test_get_repo_list(self):
		if not os.path.isdir('mcshake'):
			generator.clone_repo(self.repo_url, self.temp_dir, settings.password)
		repo_list = generator.get_repo_list(['mcshake'])
		first, last = generator.get_commit_dates('mcshake')
		current = str(datetime.now()).split('.')[0].split(' ')[0]
		self.assertEqual(repo_list, ['mcshake|' + current + '|' + first + '|' + last])


if __name__ == '__main__':
	unittest.main()
