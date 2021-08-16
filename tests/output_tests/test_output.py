import sys
import io
sys.path.append('../../src')
from output import *
import unittest
from os import remove
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from filecmp import cmp

class TestImportingFunction(unittest.TestCase):

	files_produced = []

	def __init__(self, *args, **kwargs):
		super(TestImportingFunction, self).__init__(*args, **kwargs)

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

	@classmethod
	def tearDownClass(cls):
		#Clean the files that were produced
		for file_to_be_removed in cls.files_produced:
			try:
				remove(file_to_be_removed)
			except Exception as e:
				pass

	def helper_output_testing(self, extension_parameter):
		results_to_be_outputed = self.session.execute("SELECT * FROM HASH")
		output_file_name = 'TEST_HASH.' + extension_parameter
		correct_file_name = 'HASH.' + extension_parameter
		self.assertTrue(output(results_to_be_outputed, output_file_name))
		self.files_produced.append(output_file_name)
		self.assertTrue(cmp(output_file_name, correct_file_name,shallow = False))

	def test_populate_stdout(self):
		results_to_be_outputed = self.session.execute("SELECT * FROM HASH")
		self.assertTrue(output(results_to_be_outputed, sys.stdout))
		with open('HASH.txt','r') as f:
			self.assertEqual(self.io_stream.getvalue(), f.read())

	def test_populate_txt(self):
		self.helper_output_testing('txt')

	def test_populate_csv(self):
		self.helper_output_testing('csv')

	def test_populate_tsv(self):
		self.helper_output_testing('tsv')		

	def test_populate_json(self):
		self.helper_output_testing('json')		

	def test_populate_yaml(self):
		self.helper_output_testing('yaml')		

	def test_populate_xml(self):
		self.helper_output_testing('xml')						

	def test_populate_invalid_exception(self):
		with self.assertRaises(Exception):
			populate_table(self.session, 'HASH.pdf', 'HASH', '.pdf')		

if __name__ == '__main__':
	unittest.main()