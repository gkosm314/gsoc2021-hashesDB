from sqlalchemy.orm import sessionmaker
from os.path import splitext,basename
from datetime import datetime
from hashlib import algorithms_guaranteed

from table_classes import *

def initialize_db(engine, database_path_parameter):
	"""
	Description
	-----------
	Initializes an empty hashesDB database.
	After execution, the DB_INFORMATION, SCAN_CODE and HASH_FUNCTION tables will be initialized

	Parameters
	-----------

	engine - SQLAlchemy engine object
			The engine to which the sessionmaker will be bound.

	database_path_parameter: string
			A path(relative or absolute) that specifies where the new database will be located. This has to be a path to a .db file.
			This parameter is only used to extract the name of the database, which is always the same as the name of the .db file."""

	Session = sessionmaker(bind = engine)
	session = Session()

	initialize_db_from_session(session, database_path_parameter)

def initialize_db_from_session(session_param, database_path_parameter):
	"""
	Description
	-----------
	Initializes an empty hashesDB database.
	After execution, the DB_INFORMATION, SCAN_CODE and HASH_FUNCTION tables will be initialized

	Parameters
	-----------

	session_param - SQLAlchemy session object

	database_path_parameter: string
			A path(relative or absolute) that specifies where the new database will be located. This has to be a path to a .db file.
			This parameter is only used to extract the name of the database, which is always the same as the name of the .db file."""

	initialize_db_information(session_param, database_path_parameter)
	initialize_scan_code(session_param)
	initialize_hash_function(session_param)

def initialize_db_information(session, database_path_parameter):
	"""
	Description
	-----------
	Initializes the DB_INFORMATION table, which contains information about a particular database.
	DB_INFORMATION table will contain only one row.

	Parameters
	-----------

	session - SQLAlchemy session object

	database_path_parameter: string
			A path(relative or absolute) that specifies where the new database will be located. This has to be a path to a .db file.
			This parameter is only used to extract the name of the database, which is always the same as the name of the .db file."""

	#Extract db_name from the name of the file
	filename, extension = splitext(basename(database_path_parameter))
	creation_datetime = datetime.now()

	#Initialize DB_INFORMATION table with a row
	session.add(DbInformation(db_name = filename, db_date_created = creation_datetime, db_date_modified = creation_datetime, db_version = 0, db_last_scan_id = 0))
	session.commit()

def initialize_scan_code(session):
	"""
	Description
	-----------
	Initializes the SCAN_CODE table, which contains explainations about different results of a scan.

	Parameters
	-----------
	session - SQLAlchemy session object"""

	#More scan_return_codes will be added after the scan command is implemented
	session.add_all([
		ScanCode(scan_return_code = 0, scan_return_code_description = 'Successful scan'),
		ScanCode(scan_return_code = 1, scan_return_code_description = 'Failed scan')]
		)
	session.commit()

def initialize_hash_function(session):
	"""
	Description
	-----------
	The HASH_FUNCTION table will be initialized.
	It will contain all the hash functions of the built-in hashlib python module and the ssdeep fuzzy hash.
	The SHAKE hash functions will have fixed-size. We do not support the calculation of SHAKE hashes with parameterized size.

	Parameters
	-----------

	session - SQLAlchemy session object"""

	### PYTHON BUILT-IN HASHES + XXHASHES ###

	#A dictionary containing the size(bits) of the hash functions of the built-in hashlib python module
	#Attention: SHAKE hashes can have variable size. Our tool works with the maximum size (128 bits and 256 bits respectively)
	hash_size = {'sha1': 160,
				'sha384': 384,
				'md5': 128, 
				'sha224': 224, 
				'blake2s': 256, 
				'sha3_384': 384, 
				'sha3_256': 256, 
				'sha3_224': 224, 
				'sha3_512': 512, 
				'sha256': 256, 
				'blake2b': 512, 
				'sha512': 512, 
				'shake_128': 128, 
				'shake_256': 256,
				'xxh3_64' : 64,
    			'xxh3_128': 128
				}

	#algorithms_guaranteed is imported from the built-in hashlib python module
	for hash_name in algorithms_guaranteed:
		#Produce a row for this hash
		session.add(HashFunction(hash_function_name = hash_name, hash_function_fuzzy_flag = False, hash_function_size = hash_size[hash_name]))


	### FUZZY HASHES ###

	#Create and add a row for ssdeep fuzzy function with NULL size, since ssdeep does not have a fixed size.
	session.add(HashFunction(hash_function_name = 'ssdeep', hash_function_fuzzy_flag = True, hash_function_size = None))

	#Initialize HASH_FUNCTION table by commiting the added hashes
	session.commit()