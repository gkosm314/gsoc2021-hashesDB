from sqlalchemy import MetaData
from os.path import splitext,basename
from datetime import datetime
from hashlib import algorithms_guaranteed

def initialize_db(meta, conn, database_path_parameter):
	"""def initialize_db(meta, conn, database_path_parameter):
	Parameters: meta - The Metadata() object that contains the schema information.
				conn - The connection to the engine through which we will execute the query
				database_path_parameter - The path to the database (only useful in order to extract the database name)

	Result: The DB_INFORMATION, SCAN_CODE and HASH_FUNCTION tables will be initialized"""

	initialize_db_information(meta, conn, database_path_parameter)
	initialize_scan_code(meta, conn)
	initialize_hash_function(meta, conn)

def initialize_db_information(meta, conn, database_path_parameter):
	"""def initialize_db_information(meta, conn, database_path_parameter):
	Parameters: meta - The Metadata() object that contains the schema information.
				conn - The connection to the engine through which we will execute the query
				database_path_parameter - The path to the database (only useful in order to extract the database name)

	Result: The DB_INFORMATION will be initialized"""

	#Get the db_information Table() object
	db_information = meta.tables['DB_INFORMATION']

	#Extract filename and save current time. These info will be saved in the following query
	filename, extension = splitext(basename(database_path_parameter))
	creation_datetime = datetime.now()

	#Initialize DB_INFORMATION table
	q = db_information.insert().values(db_name = filename, db_date_created = creation_datetime, db_date_modified = creation_datetime, db_version = 0, db_last_scan_id = 0)
	conn.execute(q)

def initialize_scan_code(meta, conn):
	"""def initialize_db_information(meta, conn, database_path_parameter):
	Parameters: meta - The Metadata() object that contains the schema information.
				conn - The connection to the engine through which we will execute the query

	Result: The SCAN_CODE will be initialized"""

	#Get the scan_code Table() object
	scan_code = meta.tables['SCAN_CODE']

	#Initialize SCAN_CODE table
	#TODO: More scan_return_codes will be added after the scan command is implemented
	conn.execute(scan_code.insert(), [
	   {'scan_return_code': 0, 'scan_return_code_description' : 'Successful scan'},
	   {'scan_return_code': 1, 'scan_return_code_description' : 'Failed scan'},
	])
	
def initialize_hash_function(meta, conn):
	"""def initialize_hash_function(meta, conn):
	Parameters: meta - The Metadata() object that contains the schema information.
				conn - The connection to the engine through which we will execute the query

	Result: The HASH_FUNCTION will be initialized.
			It will contain all the hash functions of the built-in hashlib python module and the ssdeep fuzzy hash.
			The SHAKE hash functions will have fixed-size. We do not support the calculation of SHAKE hashes with parameterized size."""

	#Get the hash_function Table() object
	hash_function = meta.tables['HASH_FUNCTION']

	#hash_rows is a list of dictionaries. The dictionaries have a form equivelant to a row of the HASH_FUNCTION table.
	hash_rows = []

	### PYTHON BUILT-IN HASHES ###

	#A dictionary containing the size(bits) of the hash functions of the built-in hashlib python module
	#ATTENTION: ...add note about shake hashes...
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
		new_hash_row = {
		'hash_function_name': hash_name,
		'hash_function_fuzzy_flag': False,
		'hash_function_size': hash_size[hash_name]
		}
		#and add it to the rows that will be inserted into the HASH_FUNCTION table
		hash_rows.append(new_hash_row)

	### FUZZY HASHES ###

	#Create and add a row for ssdeep fuzzy function with NULL size, since ssdeep does not have a fixed size.
	hash_rows.append({'hash_function_name': 'ssdeep','hash_function_fuzzy_flag': True,'hash_function_size': None})

	#Initialize HASH_FUNCTION table by inserting the produced rows
	conn.execute(hash_function.insert(), hash_rows)