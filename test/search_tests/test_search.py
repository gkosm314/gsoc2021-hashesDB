import sys
import io
sys.path.append('../../src')
from db import *
import unittest
from filecmp import cmp
from os import remove

class TestSearchFunction(unittest.TestCase):

	files_produced = []

	def __init__(self, *args, **kwargs):
		super(TestSearchFunction, self).__init__(*args, **kwargs)

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
				pass

	def helper_search_testing(self, hash_parameter, filename_parameter, output_path_parameter):
		correct_file = join('correct_results_txt', output_path_parameter)
		self.db.search(hash_parameter, filename_parameter, output_path_parameter)
		self.files_produced.append(output_path_parameter)
		self.assertTrue(cmp(output_path_parameter, correct_file, shallow = False))

	def test_search_single_hash(self):
		self.helper_search_testing(['swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53'], [], 'single_hash.txt')

	def test_search_multiple_hashes(self):
		self.helper_search_testing(['swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53', 'swh:1:cnt:f288702d2fa16d3cdf0035b15a9fcbc552cd88e7'], [], 'multiple_hashes.txt')

	def test_search_single_filename(self):
		self.helper_search_testing([], ['LICENSE'], 'single_filename.txt')

	def test_search_multiple_filenames(self):
		self.helper_search_testing([], ['LICENSE', 'README.md'], 'multiple_filenames.txt')

	def test_search_hash_and_filename(self):
		self.helper_search_testing(['swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53'], ['.gitignore'], 'hash_and_filename.txt')

	def test_search_no_criteria(self):
		self.helper_search_testing([], [], 'no_criteria.txt')

def main():
	unittest.main()

if __name__ == '__main__':
	main()