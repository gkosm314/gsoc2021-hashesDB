import argparse
import sys
from os import getcwd

from subcommands import *

###START OF PARSERS AND ARGUMENTS DEFINITION###

#top-level parser
parser = argparse.ArgumentParser(prog = "hashesdb", description = "Manage database that contains hash values.")
subparsers = parser.add_subparsers(description = "To print detailed help about a specific subcommand, use the -h option. For example: hashesdb search -h", help = "subcommand description")

parser.add_argument('-v','--version', action = 'version', version = '%(prog)s 1.0', help = "print the program's version")

parser.set_defaults(func=subcommand_repl)

#about subcommand parser
about_help_msg = "print information about the program"
parser_about = subparsers.add_parser('about', help = about_help_msg, description = about_help_msg)
parser_about.set_defaults(func=subcommand_about)

#schema subcommand parser
schema_help_msg = "print schema documentation"
parser_schema = subparsers.add_parser('schema', help = schema_help_msg, description = schema_help_msg)
parser_schema.set_defaults(func=subcommand_schema)

#create subcommand parser
create_help_msg = "create a hashesdb database at a given path"
parser_create = subparsers.add_parser('create', help= create_help_msg, description = create_help_msg)
parser_create.add_argument('database_path', action = "store", help = "path to the new hashesdb database (.db file)")
parser_create.add_argument('--overwrite', action='store_true', help = "flag: allows the tool to overwrite other databases when it creates a new hashesdb database")

parser_create.set_defaults(func=subcommand_create)

#import subcommand parser
import_help_msg = "create a new hashesdb database and import data saved in a file"
parser_import = subparsers.add_parser('import', help= import_help_msg, description = import_help_msg)
parser_import.add_argument('import_file_path', action = "store", help = "path to the file that will be imported (Supported file formats: CSV, TSV, JSON, YAML, XML)")
parser_import.add_argument('import_database_path', action = "store", help = "path to the new hashesdb database (.db file)")
parser_import.add_argument('--overwrite', action='store_true', help = "flag: allows the tool to overwrite other databases when it creates a new hashesdb database")

parser_import.set_defaults(func=subcommand_import)

#export subcommand parser
export_help_msg = "create a new file which contains data saved in a hashesdb database"
parser_export = subparsers.add_parser('export', help= export_help_msg, description = export_help_msg)
parser_export.add_argument('export_database_path', action = "store", help = "path to the new hashesdb database (.db file)")
parser_export.add_argument('export_file_path', action = "store", help = "path to the file that will be created (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")
parser_export.add_argument('--overwrite', action='store_true', help = "flag: allows the tool to overwrite files when it exports a hashesdb database")

parser_export.set_defaults(func=subcommand_export)

#use subcommand parser
use_help_msg = "start an interactive dialog (REPL) with the specified database in use"
parser_use = subparsers.add_parser('use', help= use_help_msg, description = use_help_msg)
parser_use.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")

parser_use.set_defaults(func=subcommand_use)

#scan subcommand parser
scan_help_msg = "calculate the hash values of the targets and insert them in the database"
parser_scan = subparsers.add_parser('scan', help= scan_help_msg, description = scan_help_msg)
parser_scan.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")
parser_scan.add_argument('-t', '--targets', nargs='+', action = "store", metavar = "TARGET", required = True, help = "targets for which the hash value will be calculated")
parser_scan.add_argument('-c', '--calculate', nargs='+', action = "store", metavar = "HASH_FUNCTION_NAME", required = True, help = "hash functions which will be used for the hash value calculation")
parser_scan.add_argument('-d', '--download-location', action = "store", metavar = "DOWNLOAD_LOCATION", default = getcwd(), help = "path to location where remote targets will be downloaded to. default: current working directory")
parser_scan.add_argument('-r', '--recursive', action = "store_true", help = "allows recursive scan of directories")
parser_scan.add_argument('-j', '--jobs', action = "store", default = 1, type = int, metavar = "THREADS_NUMBER", help = "number of threads to be used. default: 1")

parser_scan.set_defaults(func=subcommand_scan)

#search subcommand parser
#TODO: AND and OR for search. add to help
search_help_msg = "search for files based on hash value and filename. output results in specified format"
search_descr_msg = search_help_msg + ". all the criteria are seperated with a logical OR."
parser_search = subparsers.add_parser('search', help= search_help_msg, description = search_descr_msg)
parser_search.add_argument('--hash', nargs='*', action='store', metavar = "HASH_VALUE", help = "search criterion: hash value")
parser_search.add_argument('--filename', nargs='*', action='store', metavar = "FILENAME", help = "search criterion: filename")
parser_search.add_argument('-o','--output', default="sys.stdout", action='store', metavar = "OUTPUT_PATH", help = "path to output file, default: stdout (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")

parser_search.set_defaults(func=subcommand_search)

#sql subcommand parser
sql_help_msg = "execute SQL queries on specified database and output results in specified format"
parser_sql = subparsers.add_parser('sql', help= sql_help_msg, description= sql_help_msg)
parser_sql.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")
parser_sql.add_argument('sql_query_string', action = "store", help = 'an SQL query. The query must be encapsulated inside double quotation marks ("SELECT ...")')
parser_sql.add_argument('-o','--output', default= sys.stdout, action='store', metavar = "OUTPUT_PATH", help = "path to output file, default: stdout (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")

parser_sql.set_defaults(func=subcommand_sql)

#dbinfo subcommand parser
dbinfo_help_msg = "print information regarding the specified database"
parser_dbinfo = subparsers.add_parser('dbinfo', help= dbinfo_help_msg, description = dbinfo_help_msg)
parser_dbinfo.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")

parser_dbinfo.set_defaults(func=subcommand_dbinfo)

#stats subcommand parser
stats_help_msg = "print statistics regarding the specified database"
parser_stats = subparsers.add_parser('stats', help= stats_help_msg, description = stats_help_msg)
parser_stats.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")

parser_stats.set_defaults(func=subcommand_stats)

#hash-functions subcommand parser
hash_functions_msg = "print the hash functions available in the specified database"
parser_hash_functions = subparsers.add_parser('hash-functions', help= hash_functions_msg, description = hash_functions_msg)
parser_hash_functions.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")
parser_hash_functions.add_argument('--details', action='store_true', help = "prints detailed info about each hash function (size, fuzzy or not)")

parser_hash_functions.set_defaults(func=subcommand_hash_functions)

#hash-is-available subcommand parser
hash_is_available_help_msg = "check if a hash function is available in a specified database"
parser_hash_is_available = subparsers.add_parser('hash-is-available', help= hash_is_available_help_msg, description = hash_is_available_help_msg)
parser_hash_is_available.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")
parser_hash_is_available.add_argument('hash_function_name', action = "store", help = "the name of a hash function")

parser_hash_is_available.set_defaults(func=subcommand_hash_is_available)

#search-duplicates subcommand parser
search_duplicates_help_msg = "search for duplicates of a file inside a specified hashesdb database"
parser_search_duplicates = subparsers.add_parser('search-duplicates', help= search_duplicates_help_msg, description = search_duplicates_help_msg)
parser_search_duplicates.add_argument('database_path', action = "store", help = "path to a hashesdb database (.db file)")
parser_search_duplicates.add_argument('-f', '--file', nargs='+', action = "store", metavar = "FILE_PATH", required = True, help = "paths of files to look for in the specified database")

parser_search_duplicates.set_defaults(func=subcommand_search_duplicates)

#compare subcommand parser
compare_help_msg = "perform similarity comparsion with the use of fuzzy hashing"
parser_compare = subparsers.add_parser('compare', help= compare_help_msg, description = compare_help_msg)
parser_compare.add_argument('fuzzy_hash_function_name', action = "store", help = "fuzzy hash function which will be used for the similarity comparsion")
parser_compare.add_argument('-t', '--targets', nargs='+', action = "store", metavar = "TARGETS_PARAMETER", required = True, help = "targets for which the hash value will be calculated")
parser_compare.add_argument('-d', '--download-location', action = "store", metavar = "DOWNLOAD_LOCATION", default = getcwd(), help = "path to location where remote targets will be downloaded to. default: current working directory")
parser_compare.add_argument('-l', '--limit', action = "store", default = 1, type = int, metavar = "LIMIT", help = "only show results >= limit. default: 1")
parser_compare.add_argument('-r', '--recursive', action = "store_true", help = "allows recursive comparsion with the contents of directories")
parser_compare.add_argument('-o','--output', default="sys.stdout", action='store', metavar = "OUTPUT_PATH", help = "path to output file, default: stdout (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")

comparsion_args = parser_compare.add_mutually_exclusive_group(required=True)
comparsion_args.add_argument('-a','--all',help='compare targets with all the files for which the respective fuzzy hash value is stored in the database')
comparsion_args.add_argument('-c','--comparsion-targets',nargs='+', action = "store", metavar = "FILE_ID", help='compare targets with a specific file, if ')

parser_compare.set_defaults(func=subcommand_compare)

#swh subcommand parser
parser_swh = subparsers.add_parser('swh', help= "")
#TODO: fill swh arguments

parser_compare.set_defaults(func=subcommand_compare)

###END OF PARSERS AND ARGUMENTS DEFINITION###


if __name__ == '__main__':
	#parse the arguments and call the function that executes the correct subcommand
	args = parser.parse_args()
	args.func(args)