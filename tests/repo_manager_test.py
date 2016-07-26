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
import repo_manager


class RepoManagerTests(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.temp_dir = tempfile.mkdtemp()
		self.mcshake_url = 'https://'+ settings.username + '@stash.mtvi.com/scm/bot/mcshake.git'
		self.v3_url = 'https://'+ settings.username + '@stash.mtvi.com/scm/me/v3.git'

		os.chdir(self.temp_dir)

		os.system('git clone https://' 
			+ settings.username + ':' + settings.password + '@stash.mtvi.com/scm/bot/mcshake.git')
		with open(os.path.join('mcshake', 'timetag.txt'), 'wt') as timetag:
			d = str(datetime.now()).split('.')[0].split(' ')
			timetag.write(d[0])

	@classmethod
	def tearDownClass(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)

	def setUp(self):
		pass

	def tearDown(self):
		pass


	def test_get_dir_list(self):
		os.system("mkdir test_dir_1")
		os.system("mkdir test_dir_2")
		dir_list = repo_manager.get_dir_list(self.temp_dir)
		self.assertIn('test_dir_1', dir_list)
		self.assertIn('test_dir_2', dir_list)
		shutil.rmtree('test_dir_1')
		shutil.rmtree('test_dir_2')

	def test_clone_repo(self):
		repo_manager.clone_repo(self.v3_url, self.temp_dir, settings.password)
		assert os.path.isdir('v3')
		shutil.rmtree('v3')

	def test_clone_command(self):
		clone_cmd = repo_manager.get_clone_command('https://test_name@stash.mtvi.com', 'qwerty')
		self.assertEqual(clone_cmd, 'https://test_name:qwerty@stash.mtvi.com')

	def test_add_datetime(self):
		repo_manager.add_datetime(self.temp_dir)
		assert os.path.isfile('timetag.txt')
		os.remove('timetag.txt')

	def test_get_commit_dates(self):
		f_date, l_date = repo_manager.get_commit_dates(settings.repo_dir, 'mcshake')
		date_length = len(f_date.split('-'))
		self.assertEqual(date_length, 3)

	def test_get_repo_list(self):
		repo_list = repo_manager.get_repo_list(['mcshake'], self.temp_dir)
		first, last = repo_manager.get_commit_dates(self.temp_dir, 'mcshake')
		filename = os.path.join(self.temp_dir, 'mcshake', 'timetag.txt')
		with open(filename, 'rt') as timetag: latest_datetime = timetag.read()
		self.assertEqual(repo_list, ['mcshake|' + latest_datetime + '|' + first + '|' + last])


if __name__ == '__main__':
	unittest.main()