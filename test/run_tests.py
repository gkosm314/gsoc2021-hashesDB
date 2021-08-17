from os import listdir, chdir
from os.path import abspath, dirname, join
from importlib import import_module

if __name__ == '__main__':
	
	for testing_folder in listdir():
		if testing_folder == 'run_tests.py' or testing_folder == '__pycache__':
			continue
		
		testing_folder_path = abspath(testing_folder)
		testing_script_name = 'test_' + testing_folder[:-6]

		chdir(testing_folder_path)
		testing_module = import_module(testing_folder + '.' + testing_script_name)
		testing_module.main()
		chdir(dirname(testing_folder_path))	