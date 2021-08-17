import sys
import io
sys.path.append('../../src')
from db import *
import unittest
from shutil import rmtree
from filecmp import cmp
from os import listdir
from os.path import join,exists


class TestExportFunction(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super(TestExportFunction, self).__init__(*args, **kwargs)

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

	def helper_export_testing(self, extension_parameter):
		#Check if the export operation succeded
		export_dir_name = extension_parameter + '_export'
		self.assertTrue(self.db.export(export_dir_name, extension_parameter))
		
		#If the export operation was successfuly, compare the contents of the directory with the correct directory, one by one.
		#Before finishing (no matter the reason), delete the produced directory
		for file_name in listdir(export_dir_name):
			produced_file = join(export_dir_name, file_name)
			correct_file = join('correct_exports',export_dir_name + '_correct',file_name)

			#If two files are not the same then test
			try:
				files_are_the_same = cmp(produced_file, correct_file, shallow = False)
			except Exception as e:
				rmtree(export_dir_name)
				self.fail()

			if not files_are_the_same:
				rmtree(export_dir_name)
				self.fail()

		rmtree(export_dir_name)

	def test_export_parent_dir_does_not_exist(self):
		self.assertFalse(self.db.export('/fake_folder/export_folder','csv'))

	def test_export_existing_dir_without_overwrite(self):
		self.assertFalse(self.db.export('test_directory','csv'))

	def test_export_existing_dir_with_overwrite(self):
		self.db.export('test_directory','csv', overwrite_flag = True)
		self.assertFalse(exists('test_directory/hello_world.txt'))

		#Clean up
		try:
			rmtree('test_directory')
		except Exception as e:
			print(f"Error: Could not remove 'test_directory'. In more detail:")
			print(e)
		else:
			#Recreate directory
			mkdir('test_directory')
			#Recreate file
			with open("test_directory/hello_world.txt", "w") as f:
				f.write("hello world!!!")

	def test_export_invalid_extension(self):
		self.assertFalse(self.db.export('invalid_extension_dir','pdf'))

	def test_export_txt(self):
		self.helper_export_testing('txt')

	def test_export_csv(self):
		self.helper_export_testing('csv')					

	def test_export_tsv(self):
		self.helper_export_testing('tsv')

	def test_export_json(self):
		self.helper_export_testing('json')	

	def test_export_yaml(self):
		self.helper_export_testing('yaml')

	def test_export_xml(self):
		self.helper_export_testing('xml')	


def main():
	unittest.main()

if __name__ == '__main__':
	main()