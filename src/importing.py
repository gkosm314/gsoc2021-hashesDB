from sqlalchemy import text
import csv
import json
import yaml
import xml.etree.ElementTree as ET

def populate_table(session_parameter, file_path_parameter, table_name_parameter, extension_parameter):
	"""
	Description
	-----------
	Call the function that will populate the given table according to the specified file format.

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	file_path_parameter - string
		Path to the file from which the table will be populated

	table_name_parameter - string
		Name of the table that will be populated	

	extension_parameter - string
		File format from which the tables will be populated
		Supported file formats: CSV, TSV, JSON, YAML, XML
	
	Result
	-----------
	Resets the database and populates it with data stored in a different format.

	Raises
	-----------
	Raises an Exception if the given file format is not supported
	"""

	if extension_parameter == ".csv":
		populate_csv(session_parameter, file_path_parameter, table_name_parameter)
	elif extension_parameter == ".tsv":
		populate_tsv(session_parameter, file_path_parameter, table_name_parameter)
	elif extension_parameter == ".json":
		populate_json(session_parameter, file_path_parameter, table_name_parameter)
	elif extension_parameter == ".yaml":
		populate_yaml(session_parameter, file_path_parameter, table_name_parameter)
	elif extension_parameter == ".xml":
		populate_xml(session_parameter, file_path_parameter, table_name_parameter)
	else:
		raise Exception("This populate file format is not supported by hashesdb.\nSupported file formats: TXT, CSV, TSV, JSON, YAML, XML.")

	session_parameter.flush()

def populate_csv(session_parameter, file_path_parameter, table_name_parameter):
	"""
	Description
	-----------
	Reads data from csv file and insert them in a table

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	file_path_parameter - string
		Path to the file from which the table will be populated

	table_name_parameter - string
		Name of the table that will be populated	
	"""

	with open(file_path_parameter, 'r', newline='') as f:
		csv_reader = csv.reader(f)
		next(csv_reader) #Skip first line
		for row in csv_reader:
			insert_values(session_parameter, table_name_parameter, tuple(row))

def populate_tsv(session_parameter, file_path_parameter, table_name_parameter):
	"""
	Description
	-----------
	Reads data from tsv file and insert them in a table

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	file_path_parameter - string
		Path to the file from which the table will be populated

	table_name_parameter - string
		Name of the table that will be populated	
	"""

	with open(file_path_parameter, 'r', newline='') as f:
		csv_reader = csv.reader(f, dialect = 'excel-tab')
		next(csv_reader) #Skip first line
		for row in csv_reader:
			insert_values(session_parameter, table_name_parameter, tuple(row))

def populate_json(session_parameter, file_path_parameter, table_name_parameter):
	"""
	Description
	-----------
	Reads data from json file and insert them in a table

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	file_path_parameter - string
		Path to the file from which the table will be populated

	table_name_parameter - string
		Name of the table that will be populated	
	"""

	with open(file_path_parameter, 'r', newline='') as f:
		json_rows = json.load(f)	
		for row in json_rows:
			insert_values(session_parameter, table_name_parameter, dicttotuple(row))

def populate_yaml(session_parameter, file_path_parameter, table_name_parameter):
	"""
	Description
	-----------
	Reads data from yaml file and insert them in a table

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	file_path_parameter - string
		Path to the file from which the table will be populated

	table_name_parameter - string
		Name of the table that will be populated	
	"""

	with open(file_path_parameter, 'r', newline='') as f:
		yaml_rows = yaml.safe_load(f)	
		for row in yaml_rows:
			insert_values(session_parameter, table_name_parameter, dicttotuple(row))

def populate_xml(session_parameter, file_path_parameter, table_name_parameter):
	"""
	Description
	-----------
	Reads data from xml file and insert them in a table

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	file_path_parameter - string
		Path to the file from which the table will be populated

	table_name_parameter - string
		Name of the table that will be populated	
	"""

	tree_root = ET.parse(file_path_parameter).getroot()

	#Construct xml_rows (list of dicts)
	xml_rows = []
	for item in tree_root:
		new_row = dict()
		for column_tag in item:
			new_row[column_tag.tag] = column_tag.text
		xml_rows.append(new_row)

	for row in xml_rows:
		insert_values(session_parameter, table_name_parameter, dicttotuple(row))

def insert_values(session_parameter, table_name_parameter, values_tuple):
	"""
	Description
	-----------
	Insert a record in a table

	Paramaters
	-----------
	session_parameter - SQLAlchemy session object
		An active session from which we apply changes to the database

	table_name_parameter - string
		Name of the table that will be populated

	values_tuple - tuple
		A tuple with the values that will be inserted into the table. The values must be in the correct order (nth value-nth column)	
	"""

	insert_query_string = f"INSERT INTO {table_name_parameter} VALUES "
	insert_query_values = values_tuple
	insert_query = text(insert_query_string + insert_query_values)

	#Documentation of session.execute(): https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
	try:
		#Try to execute the given query
		session_parameter.execute(insert_query)
	except Exception as e:
		#If the query can't be executed, cancel the execution and print an error message
		session_parameter.rollback()
		raise e

def dicttotuple(row):
	"""
	Description
	-----------
	Gets the values of a dictionary and creates a tuple from them. 
	If a value is 'None', it is converted to NULL, so that it can be inserted in an SQLite database

	Paramaters
	-----------
	row - dictionary
	"""
	
	row_values = row.values()

	#Special handling if row contains NULL
	if None in row_values:
		tuple_from_row = tuple([v if v != None else "NULL" for v in row_values]) #This returns a tuple like this (..., 'NULL', ...) which means that NULL is a string
		str_from_tuple = str(tuple_from_row).replace("'NULL'","NULL") #This returns a tuple like this (..., NULL, ...) which means that NULL is NOT a string
	#Normal case (row does not contain NULL)
	else:
		tuple_from_row = tuple(list(row_values))
		str_from_tuple = str(tuple_from_row)

	return str_from_tuple