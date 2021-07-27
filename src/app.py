from create import is_hashesdb_database, is_valid_db_path, create as create_create
from os.path import abspath,isfile
from os import getcwd
from sys import exit as sys_exit
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

		#Set used_database to NoDb. NoDb class represents the 'no database' used state.
		self.used_database = NoDb()

		if used_database_path_param != None:
			db_absolute_path = abspath(used_database_path_param)
			try:
				#If a specific database-to-use is set, try to use it
				self.use(db_absolute_path)
			except Exception as e:
				#If you do not succeeded in using a database, then set used_database to NoDb.
				self.used_database = NoDb()
				print(e)

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
		"""
		Description
		-----------
		Exits violently with sys.exit(), without saving anything."""

		print("Exiting (no changes will be saved)...")
		sys_exit()

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
		"""
		Description
		-----------
		Implementetion of the 'use' command.
		Sets a database as the database we are currently using.
		If a database is already in use, then it prints a warning message asking the user to stop using the database he is currently using if he wants to use this database.
		Otherwise, it ensures that the file located at the given path is indeed a hashesDB database.
		If the given file does not exist, then a hashesDB database is created in order to be used.

		Parameters
		-----------
		path_param: string
			A path(relative or absolute) that specifies where the database we intend to use is located. This has to be a path to a .db file.
		
		Results
		-----------
		If we use a database when the function ends, self.used_database is a Db() object which gives us an interface to work with the database.
		Otherwise it is a NoDb() object."""

		db_absolute_path = abspath(path_param)

		#Check that no other database is currently used
		if database_is_used(self.used_database):
			print("Another database is currently used. You must stop using it before choosing another database to use.")
			print("You can stop using the database you are currently  with the 'unuse' command. You can also find out which database you currently use with the 'status' command.")
		else:
			#If the database you want to use does not exist, create it
			if not isfile(db_absolute_path):
				#self.create returns true if the database was created successfully
				print(f"No such database exists. Creating a hashesDB database at {db_absolute_path}...")
				database_exists = self.create(db_absolute_path)
			#If the database you want to use exists, make sure it is a hashesDB database
			elif is_hashesdb_database(db_absolute_path):
				database_exists = True
			else:
				print("The database you are trying to use is not a hashesDB database. This tool can only be used to manage hashesDB databases.")
				database_exists = False

			#If a hashesDB database exists (either it existed before or we just created it) then try to use it
			if database_exists:
				try:
					del self.used_database #Deletes the NoDb() object
					self.used_database = Db(db_absolute_path)
				except Exception as e:
					print("An error occured while trying to connect with the database. See more details below.")
					print(e)
					self.used_database = NoDb()
		
	def unuse(self):
		"""
		Description
		-----------
		Implementetion of the 'unuse' command.
		Checks if the database we are currently using has unsaved changes.
		If it has unsaved changes, this function prints a relative warning.
		Otherwise, it tries to delete the database we are currently.
		Finally, it sets self.used_database to a NoDb() object.

		Results
		-----------
		If the database does not have unsaved changes, then this functions sets self.used_database to a NoDb() object."""

		if not database_is_used(self.used_database):
			#You have to use a database before unusing one
			print("No database is currently used. You can begin using a database with the 'use' command.\n")
		else:
			if self.used_database.has_unsaved_changes():
				#You have to handle unsaved changes before unusing a database
				print("There are unsaved changes made in this database. You must save or cancel the changes before you unuse this database.")
				print("You can save the changes you have made with the 'save' command or you can cancel them with the 'rollback' command.\n")
			else:
				try:
					#Try to destroy the Db() object you are currently using
					del self.used_database
				except Exception as e:
					print("An error occured while trying to disconnect from the database. See more details below.")
					print(e)
				finally:
					#No matter what, after unuse, self.used_database should be a NoDb() object
					print("You are not using this database anymore.\n")
					self.used_database = NoDb()

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
		try:
			schema_documentation = open('../docs/schema_documentation.txt','r')
			print(schema_documentation.read())
		except OSError:
			print("Error: Could not open docs/schema_documentation.txt")

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


	def hash_is_available(self, hash_function_parameter):
		"""
		Description
		-----------
		Checks if the given hash function is included in the HASH_FUNCTION table.
		If there in no available hash function with this name, then it prints alternatives with similar name.

		Parameters
		-----------
		hash_function_parameter: string
			The name of the hash function whose availability we want to check 
		"""		

		self.used_database.hash_is_available(hash_function_parameter)

	def hash_functions(self, details_flag = False):
		"""
		Description
		-----------
		Implementetion of the 'hash_functions' command.
		If a database is used then it prints the hash functions available in the specified database. Otherwise it prints a warning message.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object.
		
		Parameters
		-----------
		details_flag: boolean, optional
			Default value: False
			If this parameter is True, then we print the whole HASJ_FUNCTION table of the specified database (function name, hash value size, fuzzy flag).
			Otherwise we only print the names of the available hash functions.
		"""

		self.used_database.hash_functions(details_flag)