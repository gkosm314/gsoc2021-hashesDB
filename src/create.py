import sqlite3
from sqlalchemy import create_engine,Table, Column, BigInteger, Integer, Boolean, String, Text, DateTime, MetaData, ForeignKey
from os.path import split,splitext,abspath,isdir,isfile
from os import remove

def create(database_path_parameter, overwrite_flag = False):
	"""create(database_path_parameter, overwrite_flag = False)
	Creates a hashesDB database located at database_path_parameter, if the given path is a .db file and the directory that contains it exists.
	If the file already exists, it is overwritten if overwrite_flag = True. Otherwise, an error is printed."""

	#Check if the directory exists AND if the file is a .db file.
	if not is_valid_db_path(database_path_parameter):
		return False

	#Handle .db file overwriting
	if isfile(database_path_parameter):
		if overwrite_flag:
			delete_file(database_path_parameter)
		else:	
			print(f"Error: File {database_path_parameter} already exists.")
			print("Use -overwrite flag to allow overwriting.")
			return False

	#Create the database
	try:
		create_database(database_path_parameter)
	except RuntimeError as e:
		print(e)


def is_valid_db_path(database_path_parameter):
	"""is_valid_db_path(database_path_parameter):
	Returns True if database_path_parameter is a .db file located in an existing directory. Otherwise it returns False."""
	
	#Convert parameter to absolute path, in case it is a relative path.
	database_path = abspath(database_path_parameter)

	#Check if the direcory exists.
	#If the direcotry does not exist, then sqlite will throw an error when it will try to create the new .db format.
	dir, basename = split(database_path)
	if not isdir(dir):
		print(f"Error: Directory {dir} does not exist.")
		return False
	
	#Check if the file has a .db extension.
	filename, extension = splitext(basename)
	if extension != ".db":
		print(f"Error: File {basename} is not a .db file.")
		return False

	return True
		
def delete_file(database_path_parameter):
	"""delete_file(database_path_parameter):
	Deletes a .db database file located at database_path_parameter. Raises error if the directory/file does not exist."""

	#Convert the path to absolute path in case it is relative path.
	database_path = abspath(database_path_parameter)
	try:
		remove(database_path)
	except IsADirectoryError:
		print(f"Overwrite Error: {database_path} is a directory.")
	except FileNotFoundError:
		print(f"Overwrite Error: {database_path} is not found.")
	except:
		print(f"An unexpected error occured while deleting file {database_path}.")

def create_database(database_path_parameter):
	"""create_database(database_path_parameter):
	Creates a hashesDB database located at database_path_parameter.
	If a file already exists at the given path, an exception is raised."""

	#Check if a file already exists at the given path.
	if isfile(database_path_parameter):
		raise RuntimeError("Error: Tried to create a database using the path of an already existing file")

	engine_url = "sqlite:///" + database_path_parameter

	#Create a database. The .db file will be automatically created after the first query execution
	engine = create_engine(engine_url, echo = False)
	with engine.connect() as conn:
		create_tables(engine)

def create_tables(engine):
	"""create_tables(engine):
	Creates the tables specified by the database schema and sets datatypes, primary keys and foreign keys."""

	meta = MetaData()

	#Define the tables included in the schema
	db_information = Table(
		'DB_INFORMATION', meta,
		Column('db_name', String, primary_key = True),
		Column('db_date_created', DateTime),
		Column('db_date_modified', DateTime),
		Column('db_version', Integer),
		Column('db_last_scan_id', Integer)
		)

	scan_code = Table(
		'SCAN_CODE', meta,
		Column('scan_return_code', Integer, primary_key = True),
		Column('scan_return_code_description', Integer)
		)

	scan = Table(
		'SCAN', meta,
		Column('scan_id', Integer, primary_key = True),
		Column('scan_hostname', String),
		Column('scan_command_executed', Text),
		Column('scan_date', DateTime),
		Column('scan_return_code', Integer, ForeignKey('SCAN_CODE.scan_return_code'))
		)

	file = Table(
		'FILE', meta,
		Column('file_id', Integer, primary_key = True),
		Column('scan_id', Integer, ForeignKey('SCAN.scan_id')),
		Column('file_name', String),
		Column('file_extension', String),
		Column('file_path', String),
		Column('file_size', BigInteger),
		Column('file_date_created', DateTime),
		Column('file_date_modified', DateTime),
		Column('swh_known', Boolean),
		Column('file_updated', Boolean),
		Column('origin_id', Integer, ForeignKey('ORIGIN.origin_id'))
		)

	origin = Table(
		'ORIGIN', meta,
		Column('origin_id', Integer, primary_key = True),
		Column('origin_is_local_flag', Boolean),
		Column('origin_url_or_hostname', String)
		)

	hash = Table(
		'HASH', meta,
		Column('hash_id', Integer, primary_key = True),
		Column('hash_value', String),
		Column('hash_function_name', String, ForeignKey('HASH_FUNCTION.hash_function_name')),
		Column('file_id', Integer, ForeignKey('FILE.file_id'))
		)

	hash_function = Table(
		'HASH_FUNCTION', meta,
		Column('hash_function_name', String, primary_key = True),
		Column('hash_function_fuzzy_flag', Boolean),
		Column('hash_function_size', Integer)
		)

	swh_info = Table(
		'SWH_INFO', meta,
		Column('file_id', Integer, ForeignKey('FILE.file_id')),
		Column('swh_id_core', Integer),
		Column('swh_id_qualifiers', Integer)
		)

	#Create the tables
	meta.create_all(engine)