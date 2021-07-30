from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from prettytable import PrettyTable
from os import mkdir
from os.path import abspath, isdir, join, split
from difflib import SequenceMatcher
import sys
import sqlparse
from initialize_database import initialize_db_information
from table_classes import *
#from scan import scanner
from shutil import rmtree
from output import output

Session = sessionmaker()

class Db:
	"""Db object is a object that represents a database we are currently using. It provides an interface to the App class, from which the App class can make changes to the database."""


	def __init__(self, used_database_path_param):
		"""
		Description
		-----------
		Initializes a Db() object.
		In more detail:
			-self.unsaved_changes_flag is a boolean: True if there unsaved changes in the datafase and False otherwise.
			-self.database_path is a string: the absolute path that leads to the database currently used
			-self.db_session is a SQLAlchemyORM session: the active session we use to make changes to the database

		Parameters
		-----------
		used_database_path_param: string
			A path(relative or absolute) that specifies where the database we intend to use is located. This has to be a path to a .db file.
		
		Raises
		-----------
		Raises an exception if we fail to begin a session."""

		#When the database session begins, no changes have been made
		self.unsaved_changes_flag = False
		self.database_path = abspath(used_database_path_param)

		#Create an engine and configure a session
		engine_url = "sqlite:///" + self.database_path
		engine = create_engine(engine_url, echo = False)
		Session.configure(bind=engine)

		#Try begin a session
		try:
			self.insp = inspect(engine)
			self.db_session = Session()
			self.db_session.begin()
		except Exception as e:
			raise e
		else:
			print(f"Database currently used: {self.get_database_path()}\n")

	def __del__(self):
		"""
		Description
		-----------
		Destroys a Db() object. It closes the active session.

		Raises
		-----------
		Raises an exception if we fail to close a session."""

		try:
			self.db_session.close()
		except Exception as e:
			raise Exception("Error: a problem occured while trying to disconnect from the database.")

	def get_database_path(self):
		"""
		Description
		-----------
		Returns the absolute path that leads to the database currently used """

		return self.database_path

	def has_unsaved_changes(self):
		"""
		Description
		-----------
		Should return True if there unsaved changes in the datafase and False otherwise."""

		return self.unsaved_changes_flag

	def save(self):
		"""
		Description
		-----------
		If there are unsaved changes, it saves them. Otherwise, it prints a warning message informing the user that there are no changes to save."""

		if not self.has_unsaved_changes():
			print("There are no unsaved changes to be commited")
		else:
			#Try to save the unsaved changes
			try:
				self.db_session.commit()
			except Exception as e:
				print("Error: a problem occured while trying to commit the changes to the database. In more detail:")
				print(e)
			else:
				#If save was successful, then there are no unsaved changes now.
				self.unsaved_changes_flag = False

	def rollback(self):
		"""
		Description
		-----------
		If there are unsaved changes, it cancels them. Otherwise, it prints a warning message informing the user that there are no changes to cancel."""

		if not self.has_unsaved_changes():
			print("There are no unsaved changes to cancel.")
		else:
			#Try to rollback the unsaved changes
			try:
				self.db_session.rollback()
			except Exception as e:
				print("Error: a problem occured while trying to rollback changes from the database. In more detail:")
				print(e)
			else:
				#If rollback was successful, then there are no unsaved changes now.
				self.unsaved_changes_flag = False

	def clear(self):
		"""
		Description
		-----------
		Clear the database from all its data, except the data that were inserted during the initialisation of the database."""

		print("Clearing the database...")
		try:
			self.db_session.query(Scan).delete()
			self.db_session.query(Origin).delete()
			self.db_session.query(File).delete()
			self.db_session.query(Hash).delete()
			self.db_session.query(SwhInfo).delete()
			self.db_session.query(DbInformation).delete()
			initialize_db_information(self.db_session, self.get_database_path())
		except Exception as e:
			self.db_session.rollback()
			print("Clearing the database failed...")		
		else:
			print("Cleared the database successfully.")
			self.db_session.commit()

	def dbinfo(self):
		"""
		Description
		-----------
		Prints the only row in the DB_INFORMATION table, which contains information about this particular database.."""

		try:
			dbinfo_result = self.db_session.query(DbInformation).one()
		except Exception as e:
			print("Error: a problem occured while trying to retrive information about this database. In more detail:")
			print(e)
		else:
			print(f"Database name: {dbinfo_result.db_name}")
			print(f"Date created: {dbinfo_result.db_date_created}")
			print(f"Date modified: {dbinfo_result.db_date_modified}")
			print(f"Database version: {dbinfo_result.db_version}")
			print(f"Last scan #id: {dbinfo_result.db_last_scan_id}")
			print("")

	def export(self, export_folder_path_param, export_file_format_param, overwrite_flag = False):
		"""
		Description
		-----------
		Checks if the folder in which we want to export the data already exists.
		If the folder exists and the overwrite flag is set to True, the folder is recursively deleted.
		After that, the folder is created. We obtain a list with the names of the database's tables.
		We execute a SELECT statement for each table and we obtain all of each records.
		We then export them inside the newly created folder.

		Paramaters
		-----------
		export_file_path_param - string
			Path to the folder where the table will be exported

		export_file_format_param - string
			File format in which the tables will be exported
			Supported file formats: TXT, CSV, TSV, JSON, YAML, XML

		overwrite_flag - boolean, optional
			In case a .db file exists at the given path, then if overwrite_flag = True the file will be overwritten.
			Otherwise an error message will be printed.
		
		Result
		-----------
		A folder which contains one file for each table of the database. The file has a specified format."""


		folder_abs_path = abspath(export_folder_path_param)

		parent_dir, folder_name = split(folder_abs_path)

		#Check if the parent direcory exists.
		if not isdir(parent_dir):
			print(f"Error: Directory {parent_dir} does not exist.")
			return False

		#Check if the directory we want to create exists
		if isdir(folder_abs_path):
			#If the directory exists, then overwrite it or print an error message
			if overwrite_flag:
				try:
					rmtree(folder_abs_path)
				except Exception as e:
					print(f"Error: Could not remove {folder_abs_path}. In more detail:")
					print(e)
					return False
			else:	
				print(f"Error: Directory {folder_abs_path} already exists.")
				print("Use -overwrite flag to allow overwriting.")
				return False

		#Create the directory, where the data will be exported at
		try:
			mkdir(folder_abs_path)
		except Exception as e:
			print("Error: Could not create the folder in which the exported data will be saved. In more detail:")
			print(e)
			return False

		#Get the names of the tables through the SQLAlchemy engine Inspector
		table_names_list = self.insp.get_table_names()

		#For each table, select all the records and export them to an new file (that has the specified format)
		for table_name in table_names_list:

			#Write and execute the SELECT query
			select_query_string = f"SELECT * FROM {table_name}"
			select_query = text(select_query_string)

			try:
				table_data = self.db_session.execute(select_query)
			except Exception as e:
				self.db_session.rollback()
				print("Error: an error occurred while exporting a table. In more detail:")	
				print(e)
				try:
					rmtree(folder_abs_path)
				except Exception as e:
					print(f"Error: Could not remove {folder_abs_path}. In more detail:")
					print(e)
					return False
				return False
			
			table_filename = table_name + '.' + export_file_format_param #Name of the new file is the name of the table + the extension
			table_file_path = join(folder_abs_path, table_filename) #Path of the new file

			#Output the table in the file
			output_successful_flag = output(table_data, table_file_path)
			if not output_successful_flag:
				print("Error: something went wrong during the creation of a file. Cancelling export...")
				try:
					rmtree(folder_abs_path)
				except Exception as e:
					print(f"Error: Could not remove {folder_abs_path}. In more detail:")
					print(e)
					return False

		return True


	def hash_functions(self, details_flag = False):
		"""
		Description
		-----------
		Prints the HASH_FUNCTION table, which contains information about the available hash functions.
		The function gets all the rows of the HASH_FUNCTION table and 

		Parameters
		-----------
		details_flag: boolean, optional
			Default value: False
			If this parameter is True, then we print the whole HASJ_FUNCTION table of the specified database (function name, hash value size, fuzzy flag).
			Otherwise we only print the names of the available hash functions.
		"""

		#Try to obtain data from the HASH_FUNCTION table
		try:
			hash_function_fetch = self.db_session.query(HashFunction).all()
		except Exception as e:
			print("Error: a problem occured while trying to retrive information about this database. In more detail:")
			print(e)
		else:
			print("Available hash functions:")
			#If you successfully obtain info about the hash function name, print them
			#If the details_flag is True, then print all the info you obtained from the HASH_FUNCTION table. Otherwise, print the names only.
			if details_flag:
				#Define a PrettyTable and set the headers
				hash_function_results_table = PrettyTable()
				hash_function_results_table.field_names = ["Hash function name", "Hash Value size(bits)", "Fuzzy Hash Function"]

				#Add a row to the PrettyTable for each hash function
				for row in hash_function_fetch:
					hash_function_results_table.add_row([row.hash_function_name,row.hash_function_size,row.hash_function_fuzzy_flag])
		
				#Print the PrettyTable
				print(hash_function_results_table)
			else:
				#Print the names of the hash functions
				print(*[row.hash_function_name for row in hash_function_fetch], sep = ', ')

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

		#Try to obtain data from the HASH_FUNCTION table
		try:
			hash_function_fetch = self.db_session.query(HashFunction).all()
		except Exception as e:
			print("Error: a problem occured while trying to retrive information about this database. In more detail:")
			print(e)
		else:
			#If you successfully obtain info about the hash function name, get the names and put them in a list
			available_functions = [row.hash_function_name for row in hash_function_fetch]

			#Check if the specified hash function is in the list of available hash functions 
			if hash_function_parameter in available_functions:
				#If the hash function is available, then print relative message
				print(f"Hash function {hash_function_parameter} is available in this database.")
				return True
			else:
				#If the hash function is not available, then print relative message, find hash functions with similar name
				print(f"Hash function {hash_function_parameter} is NOT available in this database.\n")

				#Find alternative hash functions that have a similar name
				alternative_hash_functions = []
				for h in available_functions:
					#Compare similarity between names. 0.6 is a threshold. High threshold => Strict when it comes to similarity
					if SequenceMatcher(None, hash_function_parameter, h).ratio() > 0.6:
						alternative_hash_functions.append(h)

				#If the alternative hash functions list is not empty, print the list
				if alternative_hash_functions:
					print("Available hash functions with similar name:")
					print(*alternative_hash_functions, sep = ', ')

				#Prompt the user to find more info about the available hash functions by using the hash-functions subcommand
				print("\nYou can use the 'hashesdb hash-functions' command to find more information about all the available hash functions.\n")
				return False		

class NoDb:
	"""NoDb object is a object that provides the same interface as the Db object. It is used when we do NOT use a database in our application."""

	def __init__(self):
		"""
		Description
		-----------
		Initializes a Db() object.
		In more detail:
			-self.unused_database_message is a string: a message that will be displayed if the user attempts to use a method that can only be applied to a Db() object.
			-self.database_path is a string: None"""

		self.unused_database_message = "Error: You have to select a database to use before running this command. You can choose a database to use with the 'use' command\n"
		self.database_path = None

	def display_unused_warning(self):
		"""
		Description
		-----------
		Prints an error message informing us that the method we try to use applies only to Db() object."""

		print(self.unused_database_message)

	def get_database_path(self):
		"""
		Description
		-----------
		Returns the absolute path that leads to the database currently used."""

		return self.database_path

	def has_unsaved_changes(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def save(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""		

		self.display_unused_warning()

	def rollback(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""	

		self.display_unused_warning()

	def clear(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def dbinfo(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def export(export_file_path_param, export_file_format_param, overwrite_flag = False):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()	

	def hash_functions(self, details_flag):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def hash_is_available(self, hash_function_parameter):
			"""
			Description
			-----------
			This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

			self.display_unused_warning()		

def database_is_used(database_object):
	"""
	Description
	-----------
	Checks if a we currently use a database by checking the type of the database_object

	Parameters
	-----------
	database_is_used:
		An object (usually either a Db() object or a NoDb() object)

	Results
	-----------
	Returns True if the given object has type 'Db'. Otherwise it returns False."""
	
	if type(database_object).__name__ == 'Db':
		return True
	else:
		return False
