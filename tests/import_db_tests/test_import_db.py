import sys
import io
sys.path.append('../../src')
from db import *
import unittest
from filecmp import cmp


class TestImportFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestImportFunction, self).__init__(*args, **kwargs)

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

	def test_import_db_path_is_not_dir(self):
		self.assertFalse(self.db.import_db('folder','csv'))

	def test_import_db_path_import_from_single_file(self):
		self.assertFalse(self.db.import_db('directory_missing_a_file/HASH.csv','csv'))		

	def test_import_db_dir_missing_a_file(self):
		self.assertFalse(self.db.import_db('directory_missing_a_file','csv'))

	def test_import_db_dir_with_one_file_different(self):
		self.assertFalse(self.db.import_db('directory_with_one_file_different','csv'))

	def test_import_db_wrong_extension(self):
		self.assertFalse(self.db.import_db('good_directory','json'))

if __name__ == '__main__':
	unittest.main()