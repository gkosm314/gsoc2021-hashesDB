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

	def test_compare_not_available_func(self):
		self.assertFalse(self.db.compare('whatever',[]))

	def test_compare_not_fuzzy_func(self):
		self.assertFalse(self.db.compare('md5',[]))						

if __name__ == '__main__':
	unittest.main()