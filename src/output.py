from os.path import split, splitext, abspath, isdir
from prettytable import PrettyTable
import sys
import csv
import json
import yaml
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString


def output(results, output_path_parameter = sys.stdout):
	"""
	Description
	-----------
	Checks if the specified directory exists. If it does not exist then it prints an error message.
	If it exists, it finds the extension of the file and calls the respective function, which will create the file and print the results.

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
		
	output_path_parameter - string  or sys.stdout, optional
		Default: sys.stdout - the result will be printed at the standard output		
		string: a path (relative or absolute) to a new file where the results will be printed
		Supported file formats: TXT,CSV, JSON, YAML, XML

	Results
	-----------
	Prints the given results in the specified format. 
	"""

	#Check if we want to print the result at the standard output
	if output_path_parameter == sys.stdout:
		output_stdout(results)
	#Otherwise:
	else:
		#Convert parameter to absolute path, in case it is a relative path.
		output_path = abspath(output_path_parameter)
		
		#Find the extension of the filename
		dir, basename = split(output_path)
		filename, extension = splitext(basename)

		#Check if the direcory exists.
		if not isdir(dir):
			print(f"Error: Directory {dir} does not exist.")
			return False

		#If the directory exist, execute the respective function accoriding to the extension of the output file
		if extension == ".txt":
			output_txt(results, output_path)
		elif extension == ".csv":
			output_csv(results, output_path)
		elif extension == ".tsv":
			output_tsv(results, output_path)
		elif extension == ".json":
			output_json(results, output_path)
		elif extension == ".yaml":
			output_yaml(results, output_path)
		elif extension == ".xml":
			output_xml(results, output_path)
		else:
			print("This output file format is not supported by hashesdb.")
			print("Supported file formats: TXT, CSV, TSV, JSON, YAML, XML.")

	return True

def results_to_dict(results):
	"""
	Description
	-----------
	Converts a Result object to a list of dictionaries

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
	
	Result
	-----------
	A list of dictionaries
	"""	

	results_list = []
	for row in results:
		results_list.append(dict(row))
	return results_list

def output_stdout(results):
	"""
	Description
	-----------
	Formats the results using the PrettyTable module and prints them at the standard output.

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
		
	output_path_parameter - string  or sys.stdout, optional
		Default: sys.stdout - the result will be printed at the standard output		
		string: a path (relative or absolute) to a new file where the results will be printed
		Supported file formats: TXT,CSV, JSON, YAML, XML
	"""	

	#Define a PrettyTable and set the headers to be equal to the names of the columns
	results_table = PrettyTable()
	results_table.field_names = results.keys()

	#Populate the PrettyTable by insreting each row
	for row in results:
		results_table.add_row(row)

	print(results_table)

def output_txt(results, txt_file_path):
	"""
	Description
	-----------
	Formats the results using the PrettyTable module.
	Creates a .txt file or overwrites an already existing one.
	Prints the results to the .txt file.

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
		
	txt_file_path - string
		string: a path (relative or absolute) to a new .txt file where the results will be printed
	"""	

	#Define a PrettyTable and set the headers to be equal to the names of the columns
	results_table = PrettyTable()
	results_table.field_names = results.keys()

	#Populate the PrettyTable by insreting each row
	for row in results:
		results_table.add_row(row)

	#Write the results
	with open(txt_file_path, 'w') as f:
		print(results_table, file = f)

def output_csv(results, csv_file_path):
	"""
	Description
	-----------
	Formats the results using the PrettyTable module.
	Creates a .csv file or overwrites an already existing one.
	Prints the results to the .csv file.

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
		
	csv_file_path - string
		string: a path (relative or absolute) to a new .csv file where the results will be printed
	"""	

	#Write the results
	with open(csv_file_path, 'w', newline='') as f:
		csv_writer = csv.writer(f)
		csv_writer.writerow(results.keys())
		csv_writer.writerows(results)

def output_tsv(results, tsv_file_path):
	"""
	Description
	-----------
	Formats the results using the PrettyTable module.
	Creates a .tsv file or overwrites an already existing one.
	Prints the results to the .tsv file.

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
		
	tsv_file_path - string
		string: a path (relative or absolute) to a new .tsv file where the results will be printed
	"""	

	#Write the results
	with open(tsv_file_path, 'w', newline='') as f:
		csv_writer = csv.writer(f, dialect = 'excel-tab')
		csv_writer.writerow(results.keys())
		csv_writer.writerows(results)

def output_json(results, json_file_path):
	"""
	Description
	-----------
	Formats the results using the PrettyTable module.
	Creates a .json file or overwrites an already existing one.
	Prints the results to the .json file.

	Parameters
	-----------
	results: sqlalchemy.engine.Result object
		Documentation page: https://docs.sqlalchemy.org/en/14/core/connections.html?highlight=result#sqlalchemy.engine.Result
		
	json_file_path - string
		string: a path (relative or absolute) to a new .json file where the results will be printed
	"""	

	#Write the results
	with open(json_file_path, 'w', newline='') as f:
		json.dump(results_to_dict(results),f)		

def output_yaml(results, yaml_file_path):
	pass

def output_xml(results, xml_file_path):
	pass