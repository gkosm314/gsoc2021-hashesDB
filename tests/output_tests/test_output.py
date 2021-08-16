import sys
import io
sys.path.append('../../src')
from output import *
import unittest
from os import remove
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from filecmp import cmp

class TestOutputFunction(unittest.TestCase):

	files_produced = []

	def __init__(self, *args, **kwargs):
		super(TestOutputFunction, self).__init__(*args, **kwargs)
		self.query_to_execute = text("SELECT * FROM HASH WHERE hash_id = 90 OR hash_id = 91")

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
		results_to_be_outputed = self.session.execute(self.query_to_execute)
		output_file_name = 'TEST_OUTPUT.' + extension_parameter
		correct_file_name = 'OUTPUT.' + extension_parameter
		self.assertTrue(output(results_to_be_outputed, output_file_name))
		self.files_produced.append(output_file_name)
		self.assertTrue(cmp(output_file_name, correct_file_name,shallow = False))

	def test_output_stdout(self):
		results_to_be_outputed = self.session.execute(self.query_to_execute)
		self.assertTrue(output(results_to_be_outputed, sys.stdout))
		with open('OUTPUT.txt','r') as f:
			self.assertEqual(self.io_stream.getvalue(), f.read())

	def test_output_txt(self):
		self.helper_output_testing('txt')

	def test_output_csv(self):
		self.helper_output_testing('csv')

	def test_output_tsv(self):
		self.helper_output_testing('tsv')		

	def test_output_json(self):
		self.helper_output_testing('json')		

	def test_output_yaml(self):
		self.helper_output_testing('yaml')		

	def test_output_xml(self):
		self.helper_output_testing('xml')						

	def test_output_invalid_extension(self):
		results_to_be_outputed = self.session.execute(self.query_to_execute)
		self.assertFalse(output(results_to_be_outputed, 'TEST_OUTPUT.pdf'))
	
	def test_output_dir_does_not_exist(self):
		results_to_be_outputed = self.session.execute(self.query_to_execute)
		self.assertFalse(output(results_to_be_outputed, 'random_directory/myfile.txt'))	

	def test_results_to_dict(self):
		results_to_be_outputed = self.session.execute(self.query_to_execute)
		self.assertEqual(results_to_dict(results_to_be_outputed),[{'hash_id': 90, 'hash_value': 'swh:1:cnt:a161b32d5e4bc17e8061a5c48a5483cd94bc7d50', 'hash_function_name': 'swhid', 'file_id': 20}, {'hash_id': 91, 'hash_value': '54aac885d92e7e1b4a14c94d07a541a99975186d', 'hash_function_name': 'sha1', 'file_id': 20}])
	
	def test_results_to_dict_empty(self):
		results_to_be_outputed = self.session.execute(text("SELECT * FROM HASH WHERE hash_id = 200"))
		self.assertEqual(results_to_dict(results_to_be_outputed),[])

if __name__ == '__main__':
	unittest.main()