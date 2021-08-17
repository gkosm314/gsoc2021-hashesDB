import sys
import io
sys.path.append('../../src')
from db import *
import unittest
from filecmp import cmp
from os import remove

class TestSqlFunction(unittest.TestCase):

	files_produced = []

	def __init__(self, *args, **kwargs):
		super(TestSqlFunction, self).__init__(*args, **kwargs)

		#Create engine
		engine_url = "sqlite:///mytest.db"
		engine = create_engine(engine_url, echo = False)   

		#Configure session
		Session = sessionmaker()
		Session.configure(bind=engine)
		self.session = Session()

		#Get the data you will be importing
		self.session.begin()
		self.data_supposed_to_be_imported = list(self.session.execute("SELECT * FROM HASH"))
		self.session.close()

	def setUp(self):
		#Suppress stdout:
		self.io_stream = io.StringIO()
		sys.stdout = self.io_stream 

		self.db = Db('mytest.db')

		#Begin session
		self.session.begin()

	def tearDown(self):
		del self.db

		#Undo the changes lose session
		self.session.rollback()
		self.session.close()

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

	def helper_sql_testing(self, sql_query_string_parameter, output_path_parameter, autocommit_flag):
		correct_file = join('correct_results_txt', output_path_parameter)
		self.db.sql_query(sql_query_string_parameter, output_path_parameter, autocommit_flag)
		self.files_produced.append(output_path_parameter)
		self.assertTrue(cmp(output_path_parameter, correct_file, shallow = False))

	def test_select_statement(self):
		sql_query_string = 'SELECT * FROM HASH'
		self.helper_sql_testing(sql_query_string, 'select_statement.txt', True)
		
	def test_delete_statement_with_autocommit(self):
		#Perform
		sql_query_string = 'DELETE FROM HASH WHERE hash_id = 1'
		self.db.sql_query(sql_query_string, 'whatever.txt', True)

		#Check
		self.assertIsNone(self.session.execute("SELECT * FROM HASH WHERE hash_id = 1").first())
		self.assertFalse(self.db.has_unsaved_changes())

		#Clean-up
		self.session.execute("INSERT INTO HASH VALUES (1, 'swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53', 'swhid',1)")
		self.session.commit()

	def test_delete_statement_without_autocommit(self):
		#Perform
		sql_query_string = 'DELETE FROM HASH WHERE hash_id = 1'
		self.db.sql_query(sql_query_string, 'whatever.txt', False)

		#Check
		self.assertIsNotNone(self.session.execute("SELECT * FROM HASH WHERE hash_id = 1").first())
		self.assertTrue(self.db.has_unsaved_changes())

	def test_statement_insert_statement(self):
		sql_query_string = 'INSERT INTO HASH VALUES (1000, "ae7069db12c4175de471f24224d7fda6",  "md5", 1)'
		self.assertFalse(self.db.sql_query(sql_query_string, 'whatever.txt', False))

	def test_statement_invalid_statement(self):
		sql_query_string = 'random string that is not a sql query'
		self.assertFalse(self.db.sql_query(sql_query_string, 'whatever.txt', False))
	

if __name__ == '__main__':
	unittest.main()