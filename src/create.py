import sqlite3
from sqlalchemy import create_engine
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
	engine = create_engine(engine_url)
	with engine.connect() as conn:
		conn.execute("CREATE DATABASE HDB;")