import sys
import io
sys.path.append('../../src')
from create import *
import unittest
from os.path import abspath, exists
from os import remove

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


class TestCreateFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCreateFunction, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

	def tearDown(self):
		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_create_relational(self):
		self.assertTrue(create('new_db.db'))
		remove('new_db.db')

	def test_create_absolute(self):
		self.assertTrue(create(abspath('new_db.db')))
		remove(abspath('new_db.db'))

	def test_create_without_overwrite(self):
		self.assertFalse(create('mytest.db'))

	def test_create_with_overwrite(self):
		self.assertTrue(create('mytest.db', overwrite_flag = True))

	def test_create_no_extension(self):
		self.assertFalse(create('mytest'))

	def test_create_bad_extension(self):
		self.assertFalse(create('mytest.pdf'))												

	def test_create_bad_directory(self):
		self.assertFalse(create('test_directory/test_directory2/mytest.pdf'))		

class TestIsValidDbFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestIsValidDbFunction, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

	def tearDown(self):
		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_is_valid_db_path_filename(self):
		self.assertTrue(is_valid_db_path('mytest.db'))

	def test_is_valid_db_path_relational(self):
		self.assertTrue(is_valid_db_path('test_directory/mytest.db'))

	def test_is_valid_db_path_absolute(self):
		self.assertTrue(is_valid_db_path(abspath('mytest.db')))

	def test_is_valid_db_path_no_extension(self):
		self.assertFalse(is_valid_db_path('mytest'))

	def test_is_valid_db_path_bad_extension(self):
		self.assertFalse(is_valid_db_path('mytest.pdf'))												

	def test_is_valid_db_path_bad_directory(self):
		self.assertFalse(is_valid_db_path('test_directory/test_directory2/mytest.pdf'))		

class TestDeleteFileFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestDeleteFileFunction, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

	def tearDown(self):

		#Recreate file
		with open("test_directory/hello_world.txt", "w") as f:
			f.write("hello world!!!")

		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_delete_file_relative(self):
		delete_file('test_directory/hello_world.txt')
		self.assertFalse(exists('test_directory/hello_world.txt'))

	def test_delete_file_absolute(self):
		delete_file(abspath('test_directory/hello_world.txt'))
		self.assertFalse(exists('test_directory/hello_world.txt'))

	def test_delete_file_is_a_directory(self):
		file_to_delete = abspath('test_directory')
		delete_file(file_to_delete)
		self.assertEqual(self.io_stream.getvalue(), f"Overwrite Error: {file_to_delete} is a directory.\n")

	def test_delete_file_file_does_not_exist(self):
		file_to_delete = abspath('whatever.txt')
		delete_file(file_to_delete)
		self.assertEqual(self.io_stream.getvalue(), f"Overwrite Error: {file_to_delete} is not found.\n")

	def test_delete_file_dir_does_not_exist(self):
		file_to_delete = abspath('whatever/hello_world.txt')
		delete_file(file_to_delete)
		self.assertEqual(self.io_stream.getvalue(), f"Overwrite Error: {file_to_delete} is not found.\n")	

class TestCreateDatabaseFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestCreateDatabaseFunction, self).__init__(*args, **kwargs)

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

	def tearDown(self):
		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_create_database(self):
		create_database('test_directory/new_database.db')
		self.assertTrue(exists('test_directory/new_database.db'))

		#Check that it is actually initialized
		try:
			engine_url = "sqlite:///test_directory/new_database.db"
			engine = create_engine(engine_url, echo = False)
			conn = engine.connect()
		except:
			self.fail("Could not connect to the database")

		db_info_initialization = conn.execute("SELECT * FROM DB_INFORMATION").first()
		scan_code_initialization = conn.execute("SELECT * FROM SCAN_CODE").first()
		hash_functions_initialization = conn.execute("SELECT * FROM HASH_FUNCTION").first()

		self.assertIsNotNone(db_info_initialization)
		self.assertIsNotNone(scan_code_initialization)
		self.assertIsNotNone(hash_functions_initialization)

		#Clean up
		remove('test_directory/new_database.db')


	def test_create_database_file_exists(self):
		with self.assertRaises(RuntimeError):
			create_database('test_directory/hello_world.txt')	

		#Recreate file
		with open("hello_world.txt", "w") as f:
			f.write("hello world!!!")	

class TestIsHashesDbDatabaseFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestIsHashesDbDatabaseFunction, self).__init__(*args, **kwargs)

		#Create engine
		engine_url = "sqlite:///mytest.db"
		engine = create_engine(engine_url, echo = False)   

		#Configure session
		Session = sessionmaker()
		Session.configure(bind=engine)
		self.session = Session()		

	def setUp(self):

		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

		#Begin session
		self.session.begin()

	def tearDown(self):

		#Undo the changes lose session
		self.session.rollback()
		self.session.close()

		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def test_is_hashesdb_database_correct(self):
		self.assertTrue(is_hashesdb_database('mytest.db'), msg = "This unit test is not independent from the database schema.")		

	def test_is_hashesdb_database_extra_column(self):
		self.assertFalse(is_hashesdb_database('extra_column_test.db'), msg = "This unit test is not independent from the database schema.")	

	def test_is_hashesdb_database_rename_column(self):
		self.assertFalse(is_hashesdb_database('rename_column_test.db'), msg = "This unit test is not independent from the database schema.")			

	def test_is_hashesdb_database_change_type_of_column(self):
		self.assertFalse(is_hashesdb_database('different_type_column_test.db'), msg = "This unit test is not independent from the database schema.")	

	def test_is_hashesdb_database_no_extension(self):
		self.assertFalse(is_hashesdb_database('mytest'))

	def test_is_hashesdb_database_bad_extension(self):
		self.assertFalse(is_hashesdb_database('mytest.pdf'))												

	def test_is_hashesdb_database_bad_directory(self):
		self.assertFalse(is_hashesdb_database('test_directory/test_directory2/mytest.pdf'))		

	def test_is_hashesdb_database_file_does_not_exist(self):
		self.assertFalse(is_hashesdb_database('mytest2.db'))		


def main():
	unittest.main()

if __name__ == '__main__':
	main()