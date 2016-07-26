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
	@classmethod
	def setUpClass(self):
		self.temp_dir = tempfile.mkdtemp()
		os.chdir(self.temp_dir)

		m = open(os.path.join(self.temp_dir, 'metrics_test.csv'), 'w')
		m.writelines(['entity,n-authors,n-revs\n', 'test.py,1,8'])
		m.close()

		os.mkdir('test')
		t = open(os.path.join('test', 'test.py'), 'w')
		t.writelines('jdlkfsj dslkjlds kkddkls')
		t.close()

	@classmethod
	def tearDownClass(self):
		os.chdir('..')
		shutil.rmtree(self.temp_dir)

	def setUp(self):
		pass

	def tearDown(self):
		pass


	def test_create_log(self):
		generator.create_log('logfile', 'v3_test', '', '', settings.v3_dir + '/.git')
		assert os.path.isfile('logfile_v3_test__.log')

	def test_run_codemaat(self):
		generator.set_path(settings.maat_dir)
		generator.create_log('logfile', 'v3_test', '', '', settings.v3_dir + '/.git')
		generator.run_codemaat('summary', 'summary_test', 'v3', '', '')
		assert os.path.isfile('summary_test_v3.csv')

	def test_generate_data_hotspots(self):
		assert os.path.isfile('test/test.py')
		generator.generate_data_hotspots('test', '2010-10-10', '2011-11-11', self.temp_dir)
		assert os.path.isfile('lines_test.csv')
		assert os.path.isfile('hotspots_test.csv')
		revs = ''
		lines = ''
		with open('hotspots_test.csv', 'rt') as csv_file:
			reader = csv.DictReader(csv_file)
			for row in reader:
				revs = row['n-revs']
				lines = row['lines']
		self.assertEqual(revs, '8')
		self.assertEqual(lines, '1')

	def test_manage_csv_folder_true(self):
		folder_name = 'test_2010-10-10_2011-11-11'
		os.mkdir(folder_name)
		self.assertTrue(generator.manage_csv_folder('test', '2010-10-10', '2011-11-11', self.temp_dir))
		shutil.rmtree(folder_name)



if __name__ == '__main__':
	unittest.main()
