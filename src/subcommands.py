from app import *

def subcommand_repl(args):
	#Start an interactive dialog
	pass

def subcommand_about(args):
	App().about()

def subcommand_schema(args):
	App().schema()

def subcommand_create(args):
	App().create(args.database_path, args.overwrite)

def subcommand_import(args):
	pass

def subcommand_export(args):
	pass

def subcommand_use(args):
	#Start an interactive dialog
	pass

def subcommand_scan(args):
	pass

def subcommand_search(args):
	pass

def subcommand_sql(args):
	App(args.database_path).sql_query(args.sql_query_string, args.output)

def subcommand_dbinfo(args):
	App(args.database_path).dbinfo()

def subcommand_stats(args):
	pass

def subcommand_hash_functions(args):
	App(args.database_path).hash_functions(args.details)

def subcommand_hash_is_available(args):
	App(args.database_path).hash_is_available(args.hash_function_name)

def subcommand_search_duplicates(args):
	pass

def subcommand_compare(args):
	pass

def subcommand_swh(args):
	pass