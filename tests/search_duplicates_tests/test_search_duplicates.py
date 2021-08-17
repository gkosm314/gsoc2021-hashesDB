import sys
import io
sys.path.append('../../src')
from db import *
import unittest
from filecmp import cmp
from os import remove
from os.path import abspath, exists, join

class TestSearchDuplicatesFunction(unittest.TestCase):

	files_produced = []

	def __init__(self, *args, **kwargs):
		super(TestSearchDuplicatesFunction, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

		self.db = Db('mytest.db')

	def tearDown(self):
		del self.db

		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	@classmethod
	def tearDownClass(cls):
		#Clean the files that were produced
		for file_to_be_removed in cls.files_produced:
			try:
				remove(file_to_be_removed)
			except Exception as e:
				print(e)

	def helper_search_duplicates_testing(self, files_list, output_path_parameter):
		correct_file = join('correct_results_txt', output_path_parameter)
		self.db.search_duplicates(files_list, output_path_parameter)
		self.files_produced.append(output_path_parameter)
		self.assertTrue(cmp(output_path_parameter, correct_file, shallow = False))

	def test_search_duplicates_single_file_relative(self):
		self.helper_search_duplicates_testing(['test_directory/LICENSE'], 'single_file.txt')

	def test_search_duplicates_single_file_absolute(self):
		self.helper_search_duplicates_testing([abspath('test_directory/LICENSE')], 'single_file_abs.txt')

	def test_search_duplicates_multiple_files(self):
		self.helper_search_duplicates_testing(['test_directory/LICENSE', 'test_directory/README.md'], 'multiple_files.txt')		

	def test_search_duplicates_file_does_not_exist(self):
		self.db.search_duplicates(['test_directory/hello_world.pdf'], 'file_does_not_exist.txt')
		self.assertFalse(exists('file_does_not_exist.txt'))

	def test_search_duplicates_file_is_directory(self):
		self.db.search_duplicates(['test_directory'], 'directory.txt')
		self.assertFalse(exists('directory.txt'))	

if __name__ == '__main__':
	unittest.main()