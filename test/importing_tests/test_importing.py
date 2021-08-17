import sys
import io
sys.path.append('../../src')
from importing import *
import unittest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class TestImportingFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestImportingFunction, self).__init__(*args, **kwargs)

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

		#Begin session
		self.session.begin()

	def tearDown(self):

		#Undo the changes lose session
		self.session.rollback()
		self.session.close()

		#Release stdout
		sys.stdout = sys.__stdout__
		self.io_stream.close()

	def helper_populate_testing(self, extension_parameter):
		#Prepare the test
		self.session.execute(text("DELETE FROM HASH"))

		#Populate the database
		populate_table(self.session, 'HASH.' + extension_parameter, 'HASH', '.' + extension_parameter)
		data_imported = list(self.session.execute(text("SELECT * FROM HASH")))
		self.assertEqual(self.data_supposed_to_be_imported, data_imported)

	def test_populate_csv(self):
		self.helper_populate_testing('csv')

	def test_populate_tsv(self):
		self.helper_populate_testing('tsv')		

	def test_populate_json(self):
		self.helper_populate_testing('json')		

	def test_populate_yaml(self):
		self.helper_populate_testing('yaml')		

	def test_populate_xml(self):
		self.helper_populate_testing('xml')						

	def test_populate_invalid_exception(self):
		with self.assertRaises(Exception):
			populate_table(self.session, 'HASH.pdf', 'HASH', '.pdf')							

	def test_insert_values(self):
		#Prepare test
		self.session.execute(text("DELETE FROM HASH WHERE hash_id = 1"))	

		#Perform action
		insert_values(self.session, 'HASH', "(1, 'swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53', 'swhid',1)")

		#Check
		row_inserted = list(self.session.execute(text("SELECT * FROM HASH WHERE hash_id = 1")))
		self.assertEqual([(1, 'swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53', 'swhid',1)], row_inserted)

	def test_insert_values_invalid_table_name(self):
		with self.assertRaises(Exception):
			insert_values(self.session, 'RANDOM_TABLE_NAME', "(1, 'swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53', 'swhid',1)")	

	def test_insert_values_invalid_tuple_not_converted_to_str(self):
		with self.assertRaises(Exception):
			insert_values(self.session, 'HASH', (1, 'swh:1:cnt:25a47ad00c7bf1a19941709c7809bd47d737ec53', 'swhid',1))

	def test_dicttotuple_without_none(self):
		dict_given_as_input = {"a": 5, "b": 6, "c": "hello world", "d": 3.14}
		self.assertEqual(dicttotuple(dict_given_as_input),"(5, 6, 'hello world', 3.14)")
												
	def test_dicttotuple_with_none(self):
		dict_given_as_input = {"a": 5, "b": None, "c": "hello world", "d": 3.14}
		self.assertEqual(dicttotuple(dict_given_as_input),"(5, NULL, 'hello world', 3.14)")												


def main():
	unittest.main()

if __name__ == '__main__':
	main()