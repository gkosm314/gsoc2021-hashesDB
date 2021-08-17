import sys
import io
sys.path.append('../../src')
from db import *
import unittest

class TestMiscDbFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestMiscDbFunction, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

		self.db = Db('mytest.db')
		self.nodb = NoDb()

	def tearDown(self):
		del self.db

		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_get_database_path_db(self):
		self.assertTrue(self.db.get_database_path(), abspath('mytest.db'))

	def test_get_database_path_no_db(self):
		self.assertIsNone(self.nodb.get_database_path())

	def test_database_is_used_db(self):
		self.assertTrue(database_is_used(self.db))	
				
	def test_database_is_used_no_db(self):
		self.assertFalse(database_is_used(self.nodb))

	def test_save_has_unsaved_changes(self):
		self.db.unsaved_changes_flag = True
		self.db.save()
		self.assertFalse(self.db.has_unsaved_changes())	

	def test_save_no_unsaved_changes(self):
		self.db.unsaved_changes_flag = False	
		self.db.save()
		self.assertFalse(self.db.has_unsaved_changes())	

	def test_rollback_has_unsaved_changes(self):
		self.db.unsaved_changes_flag = True
		self.db.rollback()
		self.assertFalse(self.db.has_unsaved_changes())	

	def test_rollback_no_unsaved_changes(self):
		self.db.unsaved_changes_flag = False
		self.db.rollback()
		self.assertFalse(self.db.has_unsaved_changes())	

def main():
	unittest.main()

if __name__ == '__main__':
	main()