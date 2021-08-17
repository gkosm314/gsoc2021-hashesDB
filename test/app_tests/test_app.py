import sys
import io
sys.path.append('../../src')
from app import *
import unittest
from os.path import exists, abspath
from os import remove

class TestAppClass(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestAppClass, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

	def tearDown(self):
		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_app_init_db_valid_path(self):
		app = App('mytest.db')	
		self.assertIsInstance(app.used_database, Db)
		self.assertFalse(app.used_database.has_unsaved_changes())

	def test_app_init_db_not_hashesdb(self):
		app = App('not_hashes_db.db')	
		self.assertIsInstance(app.used_database, NoDb)

	def test_app_init_db_invalid_path(self):
		app = App('mytest123.db')	
		self.assertIsInstance(app.used_database, NoDb)
		if exists('mytest123.db'):
			remove('mytest123.db')
			self.fail()

	def test_app_init_no_db(self):
		app = App()		
		self.assertIsInstance(app.used_database, NoDb)	

	def test_use_valid(self):
		app = App()
		app.use('mytest.db')						
		self.assertIsInstance(app.used_database, Db)
		self.assertEqual(app.used_database.get_database_path(), abspath('mytest.db'))
		self.assertFalse(app.used_database.has_unsaved_changes())

	def test_use_database_is_used(self):
		app = App('mytest.db')
		app.use('mytest2.db')
		self.assertIsInstance(app.used_database, Db)
		self.assertEqual(app.used_database.get_database_path(), abspath('mytest.db'))

	def test_use_create_db(self):
		app = App()
		app.use('new_db.db')
		self.assertTrue(exists('new_db.db'))
		self.assertFalse(app.used_database.has_unsaved_changes())
		remove('new_db.db')

	def test_use_create_db_inside_dir(self):
		app = App()
		app.use('test_directory/new_db.db')
		self.assertTrue(exists('test_directory/new_db.db'))
		remove('test_directory/new_db.db')	

	def test_use_not_hashesdb(self):
		app = App()
		app.use('not_hashes_db.db')
		self.assertIsInstance(app.used_database, NoDb)

	def test_unuse_nothing_used(self):
		app = App()
		app.unuse()
		self.assertIsInstance(app.used_database, NoDb)

	def test_unuse_no_unsaved_changes(self):
		app = App('mytest.db')
		app.unuse()
		self.assertIsInstance(app.used_database, NoDb)

	def test_unuse_has_unsaved_changes(self):
		app = App('mytest.db')
		app.used_database.unsaved_changes_flag = True
		app.unuse()
		self.assertIsInstance(app.used_database, Db)
		self.assertEqual(app.used_database.get_database_path(), abspath('mytest.db'))
		self.assertTrue(app.used_database.has_unsaved_changes())

def main():
	unittest.main()

if __name__ == '__main__':
	main()