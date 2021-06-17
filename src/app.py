from create import is_valid_db_path, create as create_create
from os.path import abspath

class App:
	#Class initialization
	def __init__(self, used_database_path_param = None):

		#By default our app runs sequentially
		self.max_threads = 1

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
				#This will probably be moved to the self.use() method
				#If you succeeded in using a database, set the appropriate flag to True.
				self.database_used_flag = True
				self.used_database_path = db_absolute_path

	def help(self, command_param = None):
		#help command implementation here...
		pass

	def version(self):
		#version command implementation here...
		pass

	def about(self):
		#about command implementation here...
		pass

	def exit(self):
		#exit command implementation here...
		#__del__ constructor will be called in here
		pass

	def threads(self,max_threads_number_parameter):
		"""def threads(self,max_threads_number_parameter):
		Parameters: max_threads_number_parameter - sets the maximum number of threads that can be used at parallel scanning

		Result: The method sets self.max_threads = max_threads_number_parameter

		Errors: Throws an error if the parameter is not an integer or if the parameter is not greater than zero."""
		try:
			max_threads_number = int(max_threads_number_parameter)
		except (TypeError, ValueError) as e:
			print("Error: max_threads parameter should be an integer.")
		else:
			if max_threads_number > 0:
				self.max_threads = max_threads_number
			else:
				print("Error: max_threads parameter should be greater than zero.")

	def create(self, path_param, overwrite_flag = False):
		create_create(path_param, overwrite_flag)

	def use(self, path_param):
		#use command implementation here...
		pass

	def unuse(self):
		#unuse command implementation here...
		pass

	def status(self):
		#status command implementation here...
		pass

	def schema(self):
		#schema command implementation here...
		pass

	def import_db(self, import_database_path_param, import_file_path_param, import_file_format_param, overwrite_flag = False):
		#import command implementation here...
		pass

	def export_db(self, export_database_path_param, export_file_path_param, export_file_format_param, overwrite_flag = False):
		#export command implementation here...
		pass
