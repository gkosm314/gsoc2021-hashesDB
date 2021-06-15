import misc_commands
from create import is_valid_db_path, create
from os.path import abspath

class app:
	#Class initialization
	#TODO = initialize max_threads
	def __init__(self, used_database_path_param = None):

		if used_database_path_param == None:
			#If no specific database-to-use is set, set the appropriate flag to False.
			self.database_used_flag = False
			self.used_database_path = None
		else:
			#If a specific database-to-use is set, try to use it
			db_absolute_path = abspath(used_database_path_param)

			try:
				self.use(db_absolute_path)
			except Exception as e:
				#If you succeeded in using a database, set the appropriate flag to False, and print an error message.
				self.database_used_flag = False
				self.used_database_path = None
				print(e)
			else:
				#If you succeeded in using a database, set the appropriate flag to True.
				self.database_used_flag = True
				self.used_database_path = db_absolute_path

	def help(command_param = None):
		#help command implementation here...
		pass

	def version():
		#version command implementation here...
		pass

	def about():
		#about command implementation here...
		pass

	def exit():
		#exit command implementation here...
		#__del__ constructor will be called in here
		pass

	def threads(max_threads_number_parameter):
		#threads command implementation here...
		pass

	def create(path_param):
		#create command implementation here...
		pass

	def use(path_param):
		#use command implementation here...
		pass

	def unuse():
		#unuse command implementation here...
		pass

	def status():
		#status command implementation here...
		pass

	def schema():
		#schema command implementation here...
		pass

	def import(import_database_path_param, import_file_path_param, import_file_format_param, overwrite_flag = False):
		#import command implementation here...
		pass

	def export(export_database_path_param, export_file_path_param, export_file_format_param, overwrite_flag = False):
		#export command implementation here...
		pass

	def hash_functions(details_flag = False):
		#hash_functions command implementation here...
		pass

	def hash_is_available(hash_name_param):
		#hash_is_available command implementation here...
		pass