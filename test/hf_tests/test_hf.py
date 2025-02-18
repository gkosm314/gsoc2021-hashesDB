import sys
import io
sys.path.append('../../src')
from db import *
import unittest

class TestHashFunctionsFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestHashFunctionsFunction, self).__init__(*args, **kwargs)

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

	def test_hash_is_available_available(self):
		self.assertTrue(self.db.hash_is_available('md5'))

	def test_hash_is_available_not_available(self):
		self.assertFalse(self.db.hash_is_available('whatever'))	

	def test_is_valid_hash_functions_valid(self):
		returned_list = self.db.valid_hash_functions(['md5','sha1','ssdeep','tlsh'])
		returned_list.sort()
		self.assertEqual(returned_list, ['md5', 'sha1', 'ssdeep', 'tlsh'])

	def test_is_valid_hash_functions_remove_duplicates(self):
		returned_list = self.db.valid_hash_functions(['md5','sha1','sha1','md5','ssdeep','tlsh'])
		returned_list.sort()
		self.assertEqual(returned_list, ['md5', 'sha1', 'ssdeep', 'tlsh'])

	def test_is_valid_hash_functions_remove_swhid(self):
		returned_list = self.db.valid_hash_functions(['md5','swhid','sha1','ssdeep','tlsh'])
		returned_list.sort()
		self.assertEqual(returned_list, ['md5', 'sha1', 'ssdeep', 'tlsh'])

	def test_is_valid_hash_functions_remove_invalid(self):
		returned_list = self.db.valid_hash_functions(['md5','sha1','whatever1','whatever2','ssdeep','tlsh'])
		returned_list.sort()
		self.assertEqual(returned_list, ['md5', 'sha1', 'ssdeep', 'tlsh'])							


def main():
	unittest.main()

if __name__ == '__main__':
	main()