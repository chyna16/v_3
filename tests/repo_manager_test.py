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
	def setUp(self):
		self.temp_dir = tempfile.mkdtemp()
		self.repo_url = 'https://'+ settings.username + '@stash.mtvi.com/scm/bot/mcshake.git'

		os.chdir(self.temp_dir)

		# sample_repo_url = stash_api.get_repo_url('mcshake', 'http')
		# repo_manager.clone_repo(self.repo_url, os.pathself.temp_dir, settings.password)

	def tearDown(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)


	def test_get_dir_list(self):
		os.system("mkdir test_dir_1")
		os.system("mkdir test_dir_2")
		dir_list = repo_manager.get_dir_list(self.temp_dir)
		self.assertIn('test_dir_1', dir_list)
		self.assertIn('test_dir_2', dir_list)
		shutil.rmtree('test_dir_1')
		shutil.rmtree('test_dir_2')

	def test_clone_repo(self):
		repo_manager.clone_repo(self.repo_url, self.temp_dir, settings.password)
		assert os.path.isdir('mcshake')
		shutil.rmtree('mcshake')

	def test_clone_command(self):
		clone_cmd = repo_manager.get_clone_command('https://test_name@stash.mtvi.com', 'qwerty')
		self.assertEqual(clone_cmd, 'https://test_name:qwerty@stash.mtvi.com')

	def test_add_datetime(self):
		repo_manager.add_datetime(self.temp_dir)
		assert os.path.isfile('timetag.txt')
		os.remove('timetag.txt')

	def test_get_commit_dates(self):
		if not os.path.isdir('mcshake'):
			repo_manager.clone_repo(self.repo_url, self.temp_dir, settings.password)
		f_date, l_date = repo_manager.get_commit_dates(settings.repo_dir, 'mcshake')
		date_length = len(f_date.split('-'))
		self.assertEqual(date_length, 3)
		shutil.rmtree('mcshake')

	def test_get_repo_list(self):
		if not os.path.isdir('mcshake'):
			repo_manager.clone_repo(self.repo_url, self.temp_dir, settings.password)
		repo_list = repo_manager.get_repo_list(['mcshake'], self.temp_dir)
		first, last = repo_manager.get_commit_dates(self.temp_dir, 'mcshake')
		filename = os.path.join(self.temp_dir, 'mcshake', 'timetag.txt')
		with open(filename, 'rt') as timetag: latest_datetime = timetag.read()
		self.assertEqual(repo_list, ['mcshake|' + latest_datetime + '|' + first + '|' + last])


if __name__ == '__main__':
	unittest.main()