from os import listdir, chdir
from os.path import abspath, dirname, join
from importlib import import_module
import unittest

if __name__ == '__main__':
	
	for testing_folder in listdir():
		if testing_folder == 'run_tests.py' or testing_folder == '__pycache__':
			continue
		
		testing_folder_path = abspath(testing_folder)
		testing_script_name = 'test_' + testing_folder[:-6]

		print('\n' + 'Testing script: ' + join(testing_folder_path,testing_script_name+'.py'))

		chdir(testing_folder_path)
		loader = unittest.TestLoader()
		tests = loader.discover('.')
		testRunner = unittest.runner.TextTestRunner()
		testRunner.run(tests)	
		chdir(dirname(testing_folder_path))	


