import sys
import io
sys.path.append('../../src')
from scan import *
from db import *
import unittest
from os.path import exists, abspath
from os import remove
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

class TestScanClass(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestScanClass, self).__init__(*args, **kwargs)

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

	def test_compute_hashes(self):
		expected_result = ['c897d1410af8f2c74fba11b1db511e9e', 'f951b101989b2c3b7471710b4e78fc4dbdfa0ca6', '3:iKFSMPG:rJPG', 'swh:1:cnt:a0423896973644771497bdc03eb99d5281615b51']
		self.assertEqual(compute_hashes('hello_world.txt', ['md5','sha1','ssdeep','tlsh']), expected_result)

	def test_compute_hashes_empty(self):
		expected_result = ['swh:1:cnt:a0423896973644771497bdc03eb99d5281615b51']
		self.assertEqual(compute_hashes('hello_world.txt', []), expected_result)		

	def test_hash_object_init_ssdeep(self):
		try:
			HashObject('ssdeep')
		except Exception as e:
			self.fail()
		
	def test_hash_object_init_tlsh(self):
		try:
			HashObject('tlsh')
		except Exception as e:
			self.fail()

	def test_hash_object_init_xxh64(self):
		try:
			HashObject('xxh64')
		except Exception as e:
			self.fail()

	def test_hash_object_init_xxh32(self):
		try:
			HashObject('xxh32')
		except Exception as e:
			self.fail()

	def test_hash_object_init_md5(self):
		try:
			HashObject('md5')
		except Exception as e:
			self.fail()

	def test_insert_hash(self):
		insert_hash(self.session, 'hello_world.txt', 'sha1', 22)
		#Check
		try:
			result_row = self.session.execute("SELECT * FROM HASH WHERE hash_id = 99").one()
		except Exception as e:
			self.fail()
		else:
			expected_result = (99, 'f951b101989b2c3b7471710b4e78fc4dbdfa0ca6', 'sha1', 22)
			self.assertEqual(result_row, expected_result)
		
	def test_insert_hash_invalid_path(self):
		with self.assertRaises(Exception):
			insert_hash(self.session, 'whatever.txt', 'sha1', 22)

def main():
	unittest.main()

if __name__ == '__main__':
	main()