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
	#initialize_scan_code implementetion here...
	pass

def initialize_hash_function(meta, conn):
	#initialize_hash_function implementetion here...
	pass