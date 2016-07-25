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


class GeneratorTests(unittest.TestCase):
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


if __name__ == '__main__':
	unittest.main()
