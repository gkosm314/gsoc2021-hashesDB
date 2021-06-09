import sqlite3
from sqlalchemy import create_engine,Table, Column, BigInteger, Integer, Boolean, String, Text, DateTime, MetaData
from os.path import split,splitext,abspath,isdir,isfile
from os import remove

def create(database_path_parameter, overwrite_flag = False):
	#Check if the directory exists and if the file is a .db file.
	if not is_valid_create_path(database_path_parameter):
		return False

	#Handle database overwriting
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


def is_valid_create_path(database_path_parameter):
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
	if isfile(database_path_parameter):
		raise RuntimeError("Error: Tried to create a database using the path of an already existing file")

	engine_url = "sqlite:///" + database_path_parameter

	#Create a database. The .db file will be automatically created after the first query execution
	engine = create_engine(engine_url, echo = False)
	with engine.connect() as conn:
		create_tables(engine)

def create_tables(engine):
	meta = MetaData()

	db_information = Table(
		'DB_INFORMATION', meta,
		Column('db_name', String, primary_key = True),
		Column('db_date_created', DateTime),
		Column('db_date_modified', DateTime),
		Column('db_version', Integer),
		Column('db_last_scan_id', Integer)
		)

	scan = Table(
		'SCAN', meta,
		Column('scan_id', Integer, primary_key = True),
		Column('scan_hostname', String),
		Column('scan_command_executed', Text),
		Column('scan_date', DateTime),
		Column('scan_return_code', Integer)
		)

	scan_code = Table(
		'SCAN_CODE', meta,
		Column('scan_return_code', Integer, primary_key = True),
		Column('scan_return_code_description', Integer)
		)

	file = Table(
		'FILE', meta,
		Column('file_id', Integer, primary_key = True),
		Column('scan_id', Integer),
		Column('file_name', String),
		Column('file_extension', String),
		Column('file_path', String),
		Column('file_size', BigInteger),
		Column('file_date_created', DateTime),
		Column('file_date_modified', DateTime),
		Column('swh_known', Boolean),
		Column('file_updated', Boolean),
		Column('origin_id', Integer)
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
		Column('hash_function_name', String),
		Column('file_id', Integer)
		)

	hash_function = Table(
		'HASH_FUNCTION', meta,
		Column('hash_function_name', String, primary_key = True),
		Column('hash_function_fuzzy_flag', Boolean),
		Column('hash_function_size', Integer)
		)

	swh_info = Table(
		'SWH_INFO', meta,
		Column('file_id', Integer),
		Column('swh_id_core', Integer),
		Column('swh_id_qualifiers', Integer)
		)

	meta.create_all(engine)