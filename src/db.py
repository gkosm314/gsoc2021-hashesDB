from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, load_only
from datetime import datetime
from prettytable import PrettyTable
from os import mkdir, listdir
from os.path import abspath, isdir, join, split, exists, getsize
from difflib import SequenceMatcher
import sys
import sqlparse
from initialize_database import initialize_db_from_session
from table_classes import *
from scan import scanner, compute_hashes, comparsion
from socket import gethostname
from shutil import rmtree
from output import output
from importing import populate_table
from itertools import combinations

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
			self.available_functions = {i[0] for i in self.db_session.query(HashFunction.hash_function_name).all()} #available hash functions 
		except Exception as e:
			raise e
		else:
			print(f"Database currently used: {self.get_database_path()}")

	def __del__(self):
		"""
		Description
		-----------
		Destroys a Db() object. It closes the active session.

		Raises
		-----------
		Raises an exception if we fail to close a session."""

		try:
			self.db_session.rollback()
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

	def reset(self, initialize_flag = True):
		"""
		Description
		-----------
		Reset the database from all its data, except the data that were inserted during the initialisation of the database.

		Paramaters
		-----------
		initialize_flag - boolean
			If True, then the database will be reinitialized.
			If False, all the tables will remain empty
		"""

		#Ask for permission
		permission = input("Are you sure you want to reset the database? All of its content will be deleted. [Y/N]")
		if not (permission == 'Y' or permission == 'y'):
			return False

		print("Reseting the database...")
		try:
			for class_name in Base.__subclasses__():
				self.db_session.query(class_name).delete()
		except Exception as e:
			self.db_session.rollback()
			print("Reseting the database failed...")	
			print(e)
			return False	
		else:
			print("Reseted the database successfully.")
			self.db_session.commit()

		if initialize_flag:
			initialize_db_from_session(self.db_session, self.get_database_path())

		return True

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

	def import_db(self, import_file_path_param, import_file_format_param):
		"""
		Description
		-----------
		Resets the database
		Checks if the folder from which we want to import the data exists.
		If the folder exists, we check that it contains exactly the files we need, in the correct format.
		If the folder is valid, we iterate though the table and we populate each table using the respective file.
		If something fails, we reset the database.

		Paramaters
		-----------
		import_file_path_param - string
			Path to the folder from which the tables will be populated

		import_file_format_param - string
			File format from which the tables will be populated
			Supported file formats: CSV, TSV, JSON, YAML, XML
		
		Result
		-----------
		Resets the database and populates it with data stored in a different format.
		"""

		#Import files extension (with dot)
		format_extension = '.' + import_file_format_param

		#Check that the file from which you want to import data is a directory
		import_path = abspath(import_file_path_param)
		if not isdir(import_path):
			print(f"Error: {import_path} is not a directory.")
			return False

		#Get the names of the tables through the SQLAlchemy engine Inspector
		tablenames_list = self.insp.get_table_names()

		#Check that the files required to complete the import exist inside the specified folder
		files_in_folder = listdir(import_path)
		for t in tablenames_list:
			table_filename = t + format_extension
			if not table_filename in files_in_folder:
				print(f"Error: No file named {table_filename} found in {import_path}.")
				print("Import failed")
				return False

		#Reset the database (without re-initilization)
		reset_flag = self.reset(False)
		if not reset_flag:
			print("Error: Could not import data in the database, since the database reset failed.")
			return False

		for t in tablenames_list:
			#For every table, search for the file that will populate it.
			table_import_path = join(import_path, t + format_extension)

			#If you cannot find it, print an error.
			if not exists(table_import_path):
				print(f"Error: Could not import data to populate table {t}. File {table_import_path} not found.")
				print("Import failed")
				self.reset()
				return False
			#Otherwise, populate the table
			else:
				try:
					populate_table(self.db_session, table_import_path, t, format_extension)
				except Exception as e:
					print(f"Importing data to table {t} failed. In more detail:")
					print(e)
					print("Import failed")
					self.reset()
					return False
				else:
					print(f"Imported data to table {t} successfully.")

		print(f"Imported data from {import_file_path_param} to database {self.get_database_path()} successfully.")

		self.db_session.commit()

	def stats(self):
		"""
		Description
		-----------
		Prints statistics about this particular database.."""

		print(f"Statistics of database {self.database_path}")

		#Initialize PrettyTable that will display the statistics regarding the database
		stats_table = PrettyTable()
		stats_table.field_names = ["Statistic", "Result"]

		#Get memory size of database
		stats_table.add_row([f"Memory size", f"{getsize(self.database_path)} bytes"])

		#Get total number of hashes
		hashes_query = self.db_session.query(Hash)
		hashes_count = hashes_query.count()
		stats_table.add_row(["Total number of hashes", f"{hashes_count} hashes"])

		#Get total number of files
		files_query = self.db_session.query(File)
		files_count = files_query.count()
		stats_table.add_row(["Total number of files", f"{files_count} files"])

		#Get percentage of SoftwareHeritage-known files
		# (no of known files/no of total files)*100 -> round so only two decimals remain -> convert to str -> concat a % symbol
		swh_known_percentage = str(round((files_query.filter(File.swh_known.is_(False)).count()/files_count)*100, 2)) + "%"
		stats_table.add_row(["Percentage of SoftwareHeritage known files", swh_known_percentage])
	
		#Align PrettyTable that displays the statistics regarding the database and print it
		stats_table.align["Statistic"] = "l"
		stats_table.align["Result"] = "r"
		print(stats_table)

		#Initialize PrettyTable that will display the statistics regarding the use of hash functions
		hash_table = PrettyTable()
		hash_table.field_names = ["Hash Function", "Number of hashes", "Percentage of total hashes"]

		#For each hash function, count the hashes that were produced from it and calculate the percentage of the total hashes
		for func_name in self.available_functions:
			func_count = hashes_query.filter(Hash.hash_function_name == func_name).count()
			func_percent = str(round((func_count/hashes_count)*100, 2)) + "%"
			hash_table.add_row([func_name, func_count, func_percent])

		#Align PrettyTable that displays the statistics regarding the use of hash functions and print it
		hash_table.align["Hash Function"] = "l"
		hash_table.align["Number of hashes"] = "c"
		hash_table.align["Percentage of total hashes"] = "r"
		hash_table.sortby = "Hash Function"
		print(hash_table)

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

	def scan(self, scan_targets_parameter, hash_functions_parameter, download_location_parameter, autocommit_flag = False, recursion_flag_parameter = True):
		"""
		Description
		-----------
		Implementetion of the 'scan' command.
		If a database is used then we scan the scan targets and updates the database. Otherwise it prints a warning message.

		Parameters
		-----------
		scan_targets_parameter: a list of lists of scan targets(strings)
			List 1: a list of local scan targets (files and directories)
			List 2: a list of Github repos
			List 3: a list of Gitlab project ids

		hash_function_parameter: list of hash function names(strings)
			hash function name: a name contained in the hash_function_name column of the HASH_FUNCTION table
		
		download_location_parameter: string
			A path(relative or absolute) to the location in which the downloaded files will be saved.
			The only files we download are remote scan targets(links to github/gitlab)

		recursion_flag_parameter: boolean, optional
			Default value: True
			If this parameter is True, then we recursively scan the contents of all the directories.
			Otherwise we do not scan the directories (we skip them).

		autocommit_parameter: boolean, optional
			Default: False
			In case this flag is set to True, the changes will be commited to the before the function ends.
			The main intention of this flag is to make sure the changes made by 'DELETE' SQL queries are saved when the sql subcommand is executed from the terminal.

			IMPORTANT NOTE: this flag is supposed to be set to True only when this method is called in order to execute a standalone command.
			If you set this parameter ro True when you execute a sql command from the REPL, it is possible that changes made before the execution
			of the SQL query will be commited too.		
		"""

		#When there are no scan parameters, do not due anything
		if not scan_targets_parameter:
			print("You should specify some scan targets to be scanned. Enter scan --help to learn more about possible scan targets.")
			return False
		
		valid_hash_functions_list = self.valid_hash_functions(hash_functions_parameter)
		
		#Retrive id of last scan from db_info
		try:
			db_info_row = self.db_session.query(DbInformation).one()
			last_scan_id = db_info_row.db_last_scan_id
		except Exception as e:
			print("Error: a problem occured while trying to start scanning this database. In more detail:")
			print(e)
			return False
		else:
			#ID of new scan = ID of last scan + 1
			new_scan_id = last_scan_id + 1

		#Info that will be stored for the scan
		new_scan_datetime = datetime.now()
		new_scan_hostname = gethostname()
		new_scan_code = 2 #Scan code for scans that are currently performed

		#Try to add the scan to the SCAN table and perform the scan
		try:
			self.db_session.add(Scan(scan_id = new_scan_id,scan_hostname = new_scan_hostname, scan_date = new_scan_datetime, scan_return_code = new_scan_code))
		except Exception as e:
			print("Error: a problem occured while trying to start scanning this database. In more detail:")
			print(e)
			return False
		else:
			new_scan_result = scanner(self.db_session, scan_targets_parameter, valid_hash_functions_list, download_location_parameter, new_scan_id, recursion_flag_parameter)
			
			db_info_row.db_last_scan_id = new_scan_id
			db_info_row.db_date_modified = datetime.now()
			new_scan_row = self.db_session.query(Scan).get(new_scan_id)
			new_scan_row.scan_return_code = new_scan_result
			self.db_session.flush()

		if autocommit_flag:
			self.db_session.commit()
			self.unsaved_changes_flag = False
		else:
			self.unsaved_changes_flag = True

	def search(self, hash_parameter, filename_parameter, output_path_parameter = sys.stdout):
		"""
		Description
		-----------
		Constructs a SQLAlchemy Query object by querying the 'File' table and appling filters.
		Converts the Query object to a string containing a SQL query and executes the aforementioned query.
		Outputs the results.

		Parameters
		-----------
		hash_parameter: list of string
			This is a list of hash values which will be used as search criteria

		filename_parameter: list of string
			This is a list of filenames which will be used as search criteria

		output_path_parameter: string
			Default: sys.stdout
			This is a path to a file, where the output will be printed/saved.
			Supported file formats: TXT, CSV, TSV, JSON, YAML, XML
		"""

		#If you have two search criteria use two filters. If you have one search criterion, use only that. If you do not have search criteria, do not use filters.
		if hash_parameter and filename_parameter:
			search_query = self.db_session.query(File).outerjoin(Hash).filter(Hash.hash_value.in_(hash_parameter), File.file_name.in_(filename_parameter)).add_columns(Hash.hash_value, Hash.hash_function_name)
		elif hash_parameter:
			search_query = self.db_session.query(File).outerjoin(Hash).filter(Hash.hash_value.in_(hash_parameter)).add_columns(Hash.hash_value, Hash.hash_function_name)
		elif filename_parameter:
			search_query = self.db_session.query(File).outerjoin(Hash).filter(File.file_name.in_(filename_parameter)).add_columns(Hash.hash_value, Hash.hash_function_name)
		else:
			search_query = self.db_session.query(File).outerjoin(Hash).add_columns(Hash.hash_value, Hash.hash_function_name)

		#search_query_text is a SQL query (string).To understand the following line, read the docs here:
		#https://docs.sqlalchemy.org/en/14/faq/sqlexpressions.html#how-do-i-render-sql-expressions-as-strings-possibly-with-bound-parameters-inlined
		search_query_text = str(search_query.statement.compile(compile_kwargs={"literal_binds": True}))

		#Try to execute the equivelant sql query
		try:
			search_results = self.db_session.execute(search_query_text)
		except Exception as e:
			#If the query can't be executed, cancel the execution and print an error message
			#We use rollback to avoid database disconnection
			self.db_session.rollback()
			print("Error: an error occurred while searching the database. In more detail:")
			print(e)
		else:
			output(search_results, output_path_parameter)
			if output_path_parameter == sys.stdout:
				print("Note: if the results do not fit in your screen, use the --output argument to print them in a new file")
		
	def sql_query(self, sql_query_string_parameter, output_path_parameter = sys.stdout, autocommit_flag = False):
		"""
		Description
		-----------
		Checks that the SQL query is either a SELECT or a DELETE query.
		Executes the SQL statement.
		
		Parameters
		-----------
		sql_query_string_parameter: string, optional
			This is a SQL query encapsulated inside double quotes (For example: "SELECT...").
			The double quotes are included in the string.		

		output_path_parameter: string
			Default: sys.stdout
			This is a path to a file, where the output will be printed/saved.
			Supported file formats: TXT,CSV, JSON, YAML, XML

		autocommit_parameter: boolean, optional
			Default: False
			In case this flag is set to True, the changes will be commited to the before the function ends.
			The main intention of this flag is to make sure the changes made by 'DELETE' SQL queries are saved when the sql subcommand is executed from the terminal.

			IMPORTANT NOTE: this flag is supposed to be set to True only when this method is called in order to execute a standalone command.
			If you set this parameter ro True when you execute a sql command from the REPL, it is possible that changes made before the execution
			of the SQL query will be commited too.			
		"""

		#This flag is True if the SQL query is a 'SELECT' query and False if it is a 'DELETE' query
		select_query_flag = True

		#Check that the string is actually a SQL query using sqlparse library
		statements = sqlparse.parse(sql_query_string_parameter)
		for statement in statements:
			if statement.get_type() != "SELECT":
				if statement.get_type() != "DELETE":
					#Neither SELECT nor DELETE, so print an error message
					print("Error: the sql command only accepts SELECT and DELETE statements")
					return False
				else:
					#Not 'SELECT' but 'DELETE', so set flag to false
					select_query_flag = False

		#Convert the string to a SQLAlchemyORM TextClause in order to execute it
		sql_text = text(sql_query_string_parameter)  

		#Documentation of session.execute(): https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		try:
			#Try to execute the given query
			sql_results = self.db_session.execute(sql_text)
		except Exception as e:
			#If the query can;t be executed, cancel the execution and print an error message
			self.db_session.rollback()
			print("Error: an error occurred while executing the SQL query. In more detail:")
			print(e)
		else:
			#If the executed query is a 'SELECT' query print the results, otherwise it is a 'DELETE' query and you should check if you should commit the changes.
			if select_query_flag:
				output(sql_results, output_path_parameter)
			elif autocommit_flag:
				self.db_session.commit()
				self.unsaved_changes_flag = False
			else:
				self.unsaved_changes_flag = True

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

	def valid_hash_functions(self, hash_functions_parameter):
		"""
		Description
		-----------
		Removes duplicates from the list of hash functions that will be calculated for each file.
		Removes SWHID since it will be calculated for every file.
		Prints error message for hash functions that are not available.

		Parameters
		-----------
		hash_function_parameter: string
			The name of the hash function whose availability we want to check 
		"""		
		valid_func_list = []

		if hash_functions_parameter:
			for h in hash_functions_parameter:
				if h == 'swhid':
					#If the hash function is SWHID, do not add it in the list that will be returned
					continue
				elif h in self.available_functions:
					#If the hash function is available, add its name in the list that will be returned
					valid_func_list.append(h)
				else:
					#If the hash function is NOT available, print an error message
					invalid_hash_msg = (f"Error: {h} is not an available hash function.\n"
					"Use the 'hash-functions' command to learn more about the available hash functions "
					"or the 'hash-is-available' command to investigate if a particular command is available.\n")
					print(invalid_hash_msg)

		#Remove duplicate hash function names
		return list(set(valid_func_list))

	def search_duplicates(self, files_list, output_path_parameter = sys.stdout):
		"""
		Description
		-----------
		Implementetion of the 'search_duplicates' command.
		If a database is used then it prints information about this database. Otherwise it prints a warning message.
		If we use a database when the function ends, self.used_database is a Db() object. Otherwise it is a NoDb() object.

		Parameters
		-----------
		files_list: list of strings
			A list of strings. The strings should be paths to files whose content we want to search for.

		output_path_parameter: string
			Default: sys.stdout
			This is a path to a file, where the output will be printed/saved.
			Supported file formats: TXT, CSV, TSV, JSON, YAML, XML	
		"""		

		#All the hashes we will look for
		hashes_of_all_files = []

		#For each file whose content you want to search for:
		for p in files_list:

			#Convert relative paths to absolute paths
			absolute_file_path = abspath(p)

			#If no sich file exists, print an error message
			if not exists(absolute_file_path):
				print(f"Error: No such file: {absolute_file_path}")
				continue
			#If the file is a directory, print an error message
			elif isdir(absolute_file_path):
				print(f"Error: {absolute_file_path} is a directory.")
				continue

			#Compute all the possible hashes for the file whose content we are searching for
			try:
				hashes_of_file = compute_hashes(absolute_file_path, self.available_functions)
			except Exception as e:
				print("Opening file {absolute_file_path} failed. This file will be excluded from the search. In more detail:")
				print(e)
			else:
				#Add the hash values you previously computed to the hashes we are going to search for
				hashes_of_all_files.extend(hashes_of_file)
			
		#Remove duplicated hash values
		hashes_to_search = list(set(hashes_of_all_files))

		if hashes_to_search:
			#Search for the hash values using the search command
			self.search(hashes_to_search, [], output_path_parameter)

	def compare(self, fuzzy_func, ids_to_compare):
		"""
		Description
		-----------
		Checks that the hash function is available and is actually a fuzzy hash function
		Checks that the given hash ids exist AND that the respective hash values were produced from the given hash function
		Compares all the valid hash values pairwise and prints the results

		Parameters
		-----------
		fuzzy_func: string
			The name of the fuzzy hash function we will use for the comparsion

		ids_to_compare - list of ints
			List of ids of Hash records (primary keys of the HASH table) 
		"""		

		#Check that the hash function is available and is actually a fuzzy hash function
		if not (fuzzy_func in self.available_functions):
			#If the hash function is NOT available, print an error message
			invalid_hash_msg = (f"Error: {fuzzy_func} is not an available hash function.\n"
			"Use the 'hash-functions' command to learn more about the available hash functions "
			"or the 'hash-is-available' command to investigate if a particular command is available.\n")
			print(invalid_hash_msg)
			return False
		else:
			#If the hash function is NOT a fuzzy hash function, print an error message
			try:
				is_fuzzy_flag = self.db_session.query(HashFunction).get(fuzzy_func).hash_function_fuzzy_flag
			except Exception as e:
				print(f"Error: Something went wrong while trying to find '{fuzzy_func}' in the HASH_FUNCTION table. In more detail:")
				print(e)
				return False
			else:
				if not is_fuzzy_flag:
					print(f"Error: '{fuzzy_func}' in not a fuzzy hash function. Use the 'hash-functions --details' command to find which fuzzy hash functions are available.")
					return False

		hashes_query = self.db_session.query(Hash)
		hashes_for_comparsion = []

		#For each hash id
		for h_id in ids_to_compare:
			h = hashes_query.get(h_id)

			#Print error message if no Hash record with such id exist
			if not h:
				print(f"Error: no Hash record with id {h_id} was found. hashesdb will skip this id.")
				continue

			#Print error message if a hash produced from a different hash function is given
			if h.hash_function_name != fuzzy_func:
				print(f"Error: Hash record with id {h_id} was not produced from '{fuzzy_func}' hash function. hashesdb will skip this hash value.")
				continue

			#If the hash id is valid, add the hash to the hashes that will be compared
			hashes_for_comparsion.append(h)

		#Compare all the pairs
		if len(hashes_for_comparsion) < 2:
			print("No pair of hashes to compare")
		else:
			comparsion_results = []

			#Compare all hashes pairwise and add the result to the comparsion_result list
			for (a,b) in combinations(hashes_for_comparsion, 2):
				print(f"[{fuzzy_func}] Comparing hash #{a.hash_id} with hash #{b.hash_id}...")
				comparsion_results.append((a.hash_id,b.hash_id,comparsion(fuzzy_func,a.hash_value,b.hash_value)))

			#Print all the comparsion results
			for (first_hash_id, second_hash_id, comparesion_value) in comparsion_results:
				print(f"[{fuzzy_func}] Comparsion between hash #{first_hash_id} and hash #{second_hash_id} = {comparesion_value}")


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

	def reset(self):
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

	def import_db(self, import_file_path_param, import_file_format_param):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()
    
	def stats(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def export(self, export_file_path_param, export_file_format_param, overwrite_flag = False):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def scan(self, scan_targets_parameter, hash_functions_parameter, download_location_parameter, autocommit_flag = False, recursion_flag_parameter = True):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def search(self, hash_parameter, filename_parameter, output_path_parameter = sys.stdout):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def sql_query(self, sql_query_string_parameter, output_path_parameter = sys.stdout):
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

	def search_duplicates(self, files_list, output_path_parameter = sys.stdout):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()
    
	def compare(self, fuzzy_func, ids_to_compare):
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