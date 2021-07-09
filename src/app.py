from create import is_hashesdb_database, is_valid_db_path, create as create_create
from os.path import abspath,isfile
from os import getcwd

from db import Db,NoDb,database_is_used

class App:
	"""
	This is the main class of our application. It provides an interface used by the parser.
	"""

	def __init__(self, used_database_path_param = None):
		"""
		Description
		-----------
		App class initializer

		Parameters
		-----------
		used_database_path_param: string, optional
			When set, the app starts and immediately tries to use a hashesDB database located at the given path(either relative or absolute path) 

		Results
		-----------
		Initializes self.max_threads, self.working_directory and self.used_database.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object."""

		#By default our app runs sequentially
		self.max_threads = 1

		#Set the working directory
		self.working_directory = getcwd()

		if used_database_path_param == None:
			#Set used_database to NoDb. NoDb class represents the 'no database' used state.
			self.used_database = NoDb()
		else:
			db_absolute_path = abspath(used_database_path_param)
			try:
				#If a specific database-to-use is set, try to use it
				self.use(db_absolute_path)
			except Exception as e:
				#If you do not succeeded in using a database, then set used_database to NoDb.
				self.used_database = NoDb()
				print(e)

	def help(self, command_param = None):
		#help command implementation here...
		pass

	def version(self):
		pass

	def about(self):
		"""
		Description
		-----------
		Implementetion of the 'about' command.
		Prints information about the project."""

		print("------------------------------------------------------------------------------------------------------------------------------------------")
		print("""
		hashesDB is a command line tool that helps users manage a database of hashes of files. It provides several database
		functionalities such as insertion, deletion and searching.It also supports fuzzy hashing, a hashing technique based
		on Locality-Sensitive Hashing that makes it possible to perform similarity	checking with the use of hashing.""")
		print("""
		The development of this project began by the Open Technologies Alliance(GFOSS) during the Google Summer of Code 2021
		program. hashesDB is licenced under the GPL-3.0 License.""")
		print("""
		If you want to report an issue or you are interested in contributing, visit:
		https://github.com/eellak/gsoc2021-hashesDB
		""")
		print("------------------------------------------------------------------------------------------------------------------------------------------")

	def exit(self):
		pass

	def threads(self,max_threads_number_parameter):
		"""
		Description
		-----------
		Implementetion of the 'threads' command.
		Sets the maximum number of threads that can be used while parallel scanning.

		Parameters
		-----------
		used_database_path_param: int
			Maximum number of threads

		Results
		-----------
		Checks if the given parameter is an integer > 0 and then changes self.max_threads to max_threads_number_parameter (in the App() class)."""

		try:
			#Try to convert the given to parameter to an integer
			max_threads_number = int(max_threads_number_parameter)
		except (TypeError, ValueError) as e:
			#If you fail, then the given parameter is not an integer
			print("Error: max_threads parameter should be an integer.")
		else:
			#If you succeed, then check that the parameter is greater than 0
			if max_threads_number > 0:
				self.max_threads = max_threads_number
			else:
				print("Error: max_threads parameter should be greater than zero.")

	def create(self, path_param, overwrite_flag = False):
		"""
		Description
		-----------
		Implementetion of the 'create' command.
		Creates a new initiliazed hashesDB database by calling the 'create' function from src/create.py. 

		Parameters
		-----------
		path_param: string
			A path(relative or absolute) that specifies where the new database will be located. This has to be a path to a .db file.
		
		overwrite_flag - boolean, optional
			In case a .db file exists at the given path, then if overwrite_flag = True the file will be overwritten.
			Otherwise an error message will be printed.

		Results
		-----------
		Returns True if the database was successfully created. Otherwise it returns False."""

		db_absolute_path = abspath(path_param)
		return create_create(db_absolute_path, overwrite_flag)

	def use(self, path_param):
		pass
		
	def unuse(self):
		pass

	def status(self):
		"""
		Description
		-----------
		Implementetion of the 'status' command.
		Prints information about the current status of the app (used database, unsaved changes, number of threads available for parallization and working directory). """

		if not database_is_used(self.used_database):
			#If there is no database currently used then inform the user
			print("No database is currently active. You can choose a database to manage with the 'use database_path' command.\n")
		else:
			#If there is a database currently used, check if there are unsaved changes waiting to be commited
			print(f"Database currently used: {self.used_database.get_database_path()}\n")
			if self.used_database.has_unsaved_changes():
				print("There are unsaved changes made regarding this database. You can commit them to the database with the 'save' command.")
			else:
				print("There are no unsaved changes made regarding this database.")

		#Print maximum threads
		print(f"Number of maximum threads allowed: {self.max_threads}\n")

		#Print maximum threads
		print(f"Working directory: {self.working_directory}\n")				


	def schema(self):
		#schema command implementation here...
		pass

	def import_db(self, import_database_path_param, import_file_path_param, import_file_format_param, overwrite_flag = False):
		#import command implementation here...
		pass

	def export_db(self, export_database_path_param, export_file_path_param, export_file_format_param, overwrite_flag = False):
		#export command implementation here...
		pass

	def save(self):
		"""
		Description
		-----------
		Implementetion of the 'save' command.
		If a database is used and it has unsaved changes then it saves them. Otherwise it prints a warning message.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object."""
		
		self.used_database.save()

	def rollback(self):
		"""
		Description
		-----------
		Implementetion of the 'rollback' command.
		If a database is used and it has unsaved changes then it cancels them. Otherwise it prints a warning message.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object."""
		
		self.used_database.rollback()

	def clear(self):
		"""
		Description
		-----------
		Implementetion of the 'clear' command.
		If a database is used then it asks for permission to drop all its data. Otherwise it prints a warning message.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object."""
		
		self.used_database.clear()

	def dbinfo(self):
		"""
		Description
		-----------
		Implementetion of the 'dbinfo' command.
		If a database is used then it prints information about this database. Otherwise it prints a warning message.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object."""

		self.used_database.dbinfo()

	def scan(self, scan_targets_parameter, hash_functions_parameter, download_location_parameter = self.working_directory, recursion_flag_parameter = True):
		"""
		Description
		-----------
		Implementetion of the 'scan' command.
		If a database is used then we scan the scan targets and updates the database. Otherwise it prints a warning message.

		Parameters
		-----------
		scan_targets_parameter: list of scan targets(strings)
			A scan target may be one of the following:
				-a path to a local file 
				-a path to a local directory
				-a Github link
				-a Gitlab link
				-a Bitbucket link

		hash_function_parameter: list of hash function names(strings)
			hash function name: a name contained in the hash_function_name column of the HASH_FUNCTION table
		
		download_location_parameter: string, optional
			Default value: the working directory
			A path(relative or absolute) to the location in which the downloaded files will be saved.
			The only files we download are remote scan targets(links to github/gitlab/bitbucket)

		recursion_flag_parameter: boolean, optional
			Default value: True
			If this parameter is True, then we recursively scan the contents of all the directories.
			Otherwise we do not scan the directories (we skip them).
		"""

		self.used_database.scan(scan_targets_parameter, hash_functions_parameter, download_location_parameter, recursion_flag_parameter)