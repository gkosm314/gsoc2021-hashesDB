import argparse
import sys
from os import getcwd
from shlex import split
from app import *

class ParserTemplate:

	'''This class contains a parser that has includes commands and arguments that are common between the standalone terminal commands and the REPL'''

	def __init__(self):
		#general parser
		self.parser = argparse.ArgumentParser(prog = "hashesdb", description = "Manage database that contains hash values.")
		self.subparsers = self.parser.add_subparsers(description = "To print detailed help about a specific subcommand, use the -h option. For example: hashesdb search -h", help = "subcommand description")
		self.parser.add_argument('-v','--version', action = 'version', version = '%(prog)s 1.0', help = "print the program's version")

		#about subcommand parser
		about_help_msg = "print information about the program"
		self.parser_about = self.subparsers.add_parser('about', help = about_help_msg, description = about_help_msg)

		#schema subcommand parser
		schema_help_msg = "print schema documentation"
		self.parser_schema = self.subparsers.add_parser('schema', help = schema_help_msg, description = schema_help_msg)	

		#create subcommand parser
		create_help_msg = "create a hashesdb database at a gien path"
		self.parser_create = self.subparsers.add_parser('create', help= create_help_msg, description = create_help_msg)
		self.parser_create.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to the new hashesdb database (.db file)")
		self.parser_create.add_argument('--overwrite', action='store_true', help = "flag: allows the tool to overwrite other databases when it creates a new hashesdb database")			

		#import subcommand parser
		import_help_msg = "create a new hashesdb database and import data saved in a file"
		self.parser_import = self.subparsers.add_parser('import', help= import_help_msg, description = import_help_msg)
		self.parser_import.add_argument('-f', '--folder', metavar = 'IMPORT_FOLDER_PATH', action = "store", help = "path to the folder that will be imported")
		self.parser_import.add_argument('-d', '--database', '--db', required = True, metavar = 'IMPORT_DATABASE_PATH', action = "store", help = "path to the new hashesdb database (.db file)")
		self.parser_import.add_argument('-e','--extension', metavar = 'IMPORT_FILE_FORMAT', action = "store", choices=['txt','csv','tsv','json','yaml','xml'], help = "Supported file formats: TXT, CSV, TSV, JSON, YAML, XML")
		self.parser_import.add_argument('--overwrite', action='store_true', help = "flag: allows the tool to overwrite other databases when it creates a new hashesdb database")

		#export subcommand parser
		export_help_msg = "create a new file which contains data saved in a hashesdb database"
		self.parser_export = self.subparsers.add_parser('export', help= export_help_msg, description = export_help_msg)
		self.parser_export.add_argument('-f', '--folder', metavar = 'EXPORT_FOLDER_PATH', action = "store", help = "path to the folder that will be created")
		self.parser_export.add_argument('-e','--extension', metavar = 'EXPORT_FILE_FORMAT', action = "store", choices=['txt','csv','tsv','json','yaml','xml'], help = "Supported file formats: TXT, CSV, TSV, JSON, YAML, XML")
		self.parser_export.add_argument('--overwrite', action='store_true', help = "flag: allows the tool to overwrite files when it exports a hashesdb database")

		#use subcommand parser
		use_help_msg = "start an interactive dialog (REPL) with the specified database in use"
		self.parser_use = self.subparsers.add_parser('use', help= use_help_msg, description = use_help_msg)
		self.parser_use.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")

		#scan subcommand parser
		scan_help_msg = "calculate the hash values of the targets and insert them in the database"
		self.parser_scan = self.subparsers.add_parser('scan', help= scan_help_msg, description = scan_help_msg)
		self.parser_scan.add_argument('-t', '--targets', nargs='+', action = "store", metavar = "TARGET", help = "targets for which the hash value will be calculated")
		self.parser_scan.add_argument('-gh','--github', nargs='+', action = "store", metavar = "GITHUB_TARGET", help = "github repos for which the hash values will be calculated")
		self.parser_scan.add_argument('-gl','--gitlab', nargs='+', action = "store", metavar = "GITLAB_TARGET", help = "gitlab repos for which the hash values will be calculated")
		self.parser_scan.add_argument('-bb','--bitbucket', nargs='+', action = "store", metavar = "BITBUCKET_TARGET", help = "bitbuckets for which the hash values will be calculated")
		self.parser_scan.add_argument('-c', '--calculate', nargs='+', action = "store", metavar = "HASH_FUNCTION_NAME", help = "hash functions which will be used for the hash value calculation")
		self.parser_scan.add_argument('-dw', '--download-location', action = "store", metavar = "DOWNLOAD_LOCATION", default = getcwd(), help = "path to location where remote targets will be downloaded to. default: current working directory")
		self.parser_scan.add_argument('-j', '--jobs', action = "store", default = 1, type = int, metavar = "THREADS_NUMBER", help = "number of threads to be used. default: 1")
		self.parser_scan.add_argument('-r', '--recursive', action = "store_true", help = "allows recursive comparsion with the contents of directories")

		#search subcommand parser
		search_help_msg = "search for files based on hash value and filename. output results in specified format"
		search_descr_msg = search_help_msg + ". all the criteria are seperated with a logical OR."
		self.parser_search = self.subparsers.add_parser('search', help= search_help_msg, description = search_descr_msg)
		self.parser_search.add_argument('--hash', nargs='*', action='store', metavar = "HASH_VALUE", help = "search criterion: hash value")
		self.parser_search.add_argument('--filename', nargs='*', action='store', metavar = "FILENAME", help = "search criterion: filename")
		self.parser_search.add_argument('-o','--output', default= sys.stdout, action='store', metavar = "OUTPUT_PATH", help = "path to output file, default: stdout (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")

		#sql subcommand parser
		sql_help_msg = "execute SQL queries on specified database and output results in specified format"
		self.parser_sql = self.subparsers.add_parser('sql', help= sql_help_msg, description= sql_help_msg)
		self.parser_sql.add_argument('-q','--query', required = True, metavar = 'SQL_QUERY_STRING', action = "store", help = 'an SQL query. The query must be encapsulated inside double quotation marks ("SELECT ...")')
		self.parser_sql.add_argument('-o','--output', default= sys.stdout, action='store', metavar = "OUTPUT_PATH", help = "path to output file, default: stdout (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")

		#dbinfo subcommand parser
		dbinfo_help_msg = "print information regarding the specified database"
		self.parser_dbinfo = self.subparsers.add_parser('dbinfo', help= dbinfo_help_msg, description = dbinfo_help_msg)

		#stats subcommand parser
		stats_help_msg = "print statistics regarding the specified database"
		self.parser_stats = self.subparsers.add_parser('stats', help= stats_help_msg, description = stats_help_msg)

		#hash-functions subcommand parser
		hash_functions_msg = "print the hash functions available in the specified database"
		self.parser_hash_functions = self.subparsers.add_parser('hash-functions', help= hash_functions_msg, description = hash_functions_msg)
		self.parser_hash_functions.add_argument('--details', action='store_true', help = "prints detailed info about each hash function (size, fuzzy or not)")

		#hash-is-available subcommand parser
		hash_is_available_help_msg = "check if a hash function is available in a specified database"
		self.parser_hash_is_available = self.subparsers.add_parser('hash-is-available', help= hash_is_available_help_msg, description = hash_is_available_help_msg)
		self.parser_hash_is_available.add_argument('-func','--hash_function_name', metavar = "HASH_FUNCTION_NAME", action = "store", required = True, help = "the name of a hash function")

		#search-duplicates subcommand parser
		search_duplicates_help_msg = "search for duplicates of a file inside a specified hashesdb database"
		self.parser_search_duplicates = self.subparsers.add_parser('search-duplicates', help= search_duplicates_help_msg, description = search_duplicates_help_msg)
		self.parser_search_duplicates.add_argument('-f', '--file', nargs='+', action = "store", metavar = "FILE_PATH", required = True, help = "paths of files to look for in the specified database")

		#compare subcommand parser
		compare_help_msg = "perform similarity comparsion with the use of fuzzy hashing"
		self.parser_compare = self.subparsers.add_parser('compare', help= compare_help_msg, description = compare_help_msg)
		self.parser_compare.add_argument('-fuzzy', metavar = 'FUZZY_HASH_FUNCTION_NAME', required = True, action = "store", help = "fuzzy hash function which will be used for the similarity comparsion")
		self.parser_compare.add_argument('-ids', '--hash-ids', nargs='+', action = "store", metavar = "HASH_ID", required = True, help = "hash ids that will be compared with each other. must be products of the same fuzzy hash function")
		self.parser_compare.add_argument('-o','--output', default="sys.stdout", action='store', metavar = "OUTPUT_PATH", help = "path to output file, default: stdout (Supported file formats: TXT, CSV, TSV, JSON, YAML, XML)")

		#reset subcommand parser
		reset_help_msg = "resets database by deleting all of its content"
		self.parser_reset = self.subparsers.add_parser('reset', help= reset_help_msg, description = reset_help_msg)

	def parse(self, arg_list = None):
		#parse the arguments and call the function that executes the correct subcommand
		try:
			args = self.parser.parse_args(arg_list)
		except SystemExit as e:
		#if the arguments are wrong, then don't exit 
			print()
		else:
			try:
				args.func(args)
			except Exception as e:
				print("Error: something went wrong during the execution of the command. In more detail:")
				print(e)


class TerminalParser(ParserTemplate):

	'''This class inherits the parser of the ParserTemplate class and adds special arguments that are needed for the standalone (terminal)
	commands only. It also impements the methods that call the App() methods with the correct parameters for each standalone command.'''

	def __init__(self):

		super(TerminalParser, self).__init__()
		
		##Terminal-only subcommands

		self.parser_export.add_argument('-d', '--database', '--db', required = True, metavar = 'EXPORT_DATABASE_PATH', action = "store", help = "path to the new hashesdb database (.db file)")
		self.parser_scan.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_search.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_sql.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_dbinfo.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_stats.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_hash_functions.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_hash_is_available.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_search_duplicates.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_compare.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")
		self.parser_reset.add_argument('-d', '--database', '--db', required = True, metavar = "DATABASE_PATH", action = "store", help = "path to a hashesdb database (.db file)")

		#set defaults to TerminalParser methods
		self.parser.set_defaults(func=self.subcommand_repl)
		self.parser_about.set_defaults(func=self.subcommand_about)
		self.parser_schema.set_defaults(func=self.subcommand_schema)
		self.parser_create.set_defaults(func=self.subcommand_create)
		self.parser_import.set_defaults(func=self.subcommand_import)
		self.parser_export.set_defaults(func=self.subcommand_export)
		self.parser_use.set_defaults(func=self.subcommand_use)
		self.parser_scan.set_defaults(func=self.subcommand_scan)
		self.parser_search.set_defaults(func=self.subcommand_search)
		self.parser_sql.set_defaults(func=self.subcommand_sql)
		self.parser_dbinfo.set_defaults(func=self.subcommand_dbinfo)
		self.parser_stats.set_defaults(func=self.subcommand_stats)
		self.parser_hash_functions.set_defaults(func=self.subcommand_hash_functions)
		self.parser_hash_is_available.set_defaults(func=self.subcommand_hash_is_available)
		self.parser_search_duplicates.set_defaults(func=self.subcommand_search_duplicates)
		self.parser_compare.set_defaults(func=self.subcommand_compare)
		self.parser_reset.set_defaults(func=self.subcommand_reset)

	def subcommand_repl(self,args):
		#Open a REPL with no used database
		repl = ReplParser()
		repl.read()

	def subcommand_about(self,args):
		App().about()

	def subcommand_schema(self,args):
		App().schema()

	def subcommand_create(self,args):
		App().create(args.database, args.overwrite)

	def subcommand_import(self,args):
		pass

	def subcommand_export(self,args):
		App(args.database).export_db(args.folder, args.extension, args.overwrite)

	def subcommand_use(self,args):
		#Open a REPL and begin using the specified database
		repl = ReplParser(args.database)
		repl.read()

	def subcommand_scan(self,args):
		scan_targets = [args.targets, args.github, args.gitlab, args.bitbucket]
		App(args.database).scan(scan_targets, args.calculate, args.download_location, args.jobs, True, args.recursive)

	def subcommand_search(self,args):
		App(args.database).search(args.hash, args.filename, args.output)

	def subcommand_sql(self,args):
		App(args.database).sql_query(args.query, args.output, True)

	def subcommand_dbinfo(self,args):
		App(args.database).dbinfo()

	def subcommand_stats(self,args):
		App(args.database).stats()

	def subcommand_hash_functions(self,args):
		App(args.database).hash_functions(args.details)

	def subcommand_hash_is_available(self,args):
		App(args.database).hash_is_available(args.hash_function_name)

	def subcommand_search_duplicates(self,args):
		pass

	def subcommand_compare(self,args):
		pass

	def subcommand_reset(self,args):
		App(args.database).reset()
		
		
class ReplParser(ParserTemplate):

	'''This class inherits the parser of the ParserTemplate class and adds special commands arguments that are needed for the REPL
	It also impements the methods that call the App() methods with the correct parameters for each REPL command.'''

	def __init__(self, database_to_use_parameter = None):

		super(ReplParser, self).__init__()

		##define an App object where the given commands will be applied.
		if database_to_use_parameter == None:
			self.app = App()
		else:
			self.app = App()
			self.app.use(database_to_use_parameter)

		##REPL-only subcommands
		#exit subcommand parser
		exit_help_msg = "terminates the program"
		self.parser_exit = self.subparsers.add_parser('exit', help= exit_help_msg, description = exit_help_msg)

		#threads subcommand parser
		threads_help_msg = "sets an upperbound regarding the threads the programm can use"
		self.parser_threads = self.subparsers.add_parser('threads', help= threads_help_msg, description = threads_help_msg)
		self.parser_threads.add_argument('-j', '--jobs', action = "store", default = 1, type = int, metavar = "THREADS_NUMBER", help = "number of threads to be used. default: 1")

		#unuse subcommand parser
		unuse_help_msg = "stop using the currently used database"
		self.parser_unuse = self.subparsers.add_parser('unuse', help= unuse_help_msg, description = unuse_help_msg)

		#status subcommand parser
		status_help_msg = "prints information about the current state of the app (currently used database etc)"
		self.parser_status = self.subparsers.add_parser('status', help= status_help_msg, description = status_help_msg)

		#save subcommand parser
		save_help_msg = "commits unsaved changes to the database"
		self.parser_save = self.subparsers.add_parser('save', help= save_help_msg, description = save_help_msg)

		#rollback subcommand parser
		rollback_help_msg = "rolls back any changes to the database since the last call to 'save'"
		self.parser_rollback = self.subparsers.add_parser('rollback', help= rollback_help_msg, description = rollback_help_msg)

		##set defaults to ReplParser methods
		self.parser_about.set_defaults(func=self.repl_about)
		self.parser_schema.set_defaults(func=self.repl_schema)
		self.parser_create.set_defaults(func=self.repl_create)
		self.parser_import.set_defaults(func=self.repl_import)
		self.parser_export.set_defaults(func=self.repl_export)
		self.parser_use.set_defaults(func=self.repl_use)
		self.parser_scan.set_defaults(func=self.repl_scan)
		self.parser_search.set_defaults(func=self.repl_search)
		self.parser_sql.set_defaults(func=self.repl_sql)
		self.parser_dbinfo.set_defaults(func=self.repl_dbinfo)
		self.parser_stats.set_defaults(func=self.repl_stats)
		self.parser_hash_functions.set_defaults(func=self.repl_hash_functions)
		self.parser_hash_is_available.set_defaults(func=self.repl_hash_is_available)
		self.parser_search_duplicates.set_defaults(func=self.repl_search_duplicates)
		self.parser_compare.set_defaults(func=self.repl_compare)

		self.parser_exit.set_defaults(func=self.repl_exit)
		self.parser_threads.set_defaults(func=self.repl_threads)
		self.parser_unuse.set_defaults(func=self.repl_unuse)
		self.parser_status.set_defaults(func=self.repl_status)
		self.parser_save.set_defaults(func=self.repl_save)
		self.parser_rollback.set_defaults(func=self.repl_rollback)
		self.parser_reset.set_defaults(func=self.repl_reset)

	def read(self):
		#Read-eval-loop
		while True:
			try:
				argument_input = input(">> ")
			except EOFError:
				print()
				self.app.exit()
			else:
			    argument_list = split(argument_input)
			    self.parse(argument_list)	#parse is inherited by TemplateParser

	def repl_about(self,args):
		self.app.about()

	def repl_schema(self,args):
		self.app.schema()

	def repl_create(self,args):
		self.app.create(args.database, args.overwrite)

	def repl_import(self,args):
		pass

	def repl_export(self,args):
		self.app.export_db(args.folder, args.extension, args.overwrite)

	def repl_use(self,args):
		self.app.use(args.database)

	def repl_scan(self,args):
		scan_targets = [args.targets, args.github, args.gitlab, args.bitbucket]
		self.app.scan(scan_targets, args.calculate, args.download_location, args.jobs, False, args.recursive)

	def repl_search(self,args):
		self.app.search(args.hash, args.filename, args.output)

	def repl_sql(self,args):
		self.app.sql_query(args.query, args.output, False)

	def repl_dbinfo(self,args):
		self.app.dbinfo()

	def repl_stats(self,args):
		self.app.stats()

	def repl_hash_functions(self,args):
		self.app.hash_functions(args.details)

	def repl_hash_is_available(self,args):
		self.app.hash_is_available(args.hash_function_name)

	def repl_search_duplicates(self,args):
		pass

	def repl_compare(self,args):
		pass


	def repl_exit(self,args):
		self.app.exit()

	def repl_threads(self,args):
		self.app.threads(args.jobs)

	def repl_unuse(self,args):
		self.app.unuse()

	def repl_status(self,args):
		self.app.status()

	def repl_save(self,args):
		self.app.save()

	def repl_rollback(self,args):
		self.app.rollback()

	def repl_reset(self,args):
		self.app.reset()

if __name__ == '__main__':
	TerminalParser().parse()