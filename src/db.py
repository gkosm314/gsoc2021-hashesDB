from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import abspath

from initialize_database import initialize_db_information
from table_classes import *

Session = sessionmaker()

class Db:
	"""Db object is a object that represents a database we are currently using. It provides an interface to the App class, from which the App class can make changes to the database."""


	def __init__(self, used_database_path_param):
		"""
		Description
		-----------
		Initializes a Db() object.
		In more detail:
			-self.unsaved_changes_flag is a boolean: True if there unsaved changes in the datafase and False otherwise.
			-self.database_path is a string: the absolute path that leads to the database currently used
			-self.db_session is a SQLAlchemyORM session: the active session we use to make changes to the database

		Parameters
		-----------
		used_database_path_param: string
			A path(relative or absolute) that specifies where the database we intend to use is located. This has to be a path to a .db file.
		
		Raises
		-----------
		Raises an exception if we fail to begin a session."""

		#When the database session begins, no changes have been made
		self.unsaved_changes_flag = False
		self.database_path = abspath(used_database_path_param)

		#Create an engine and configure a session
		engine_url = "sqlite:///" + self.database_path
		engine = create_engine(engine_url, echo = False)
		Session.configure(bind=engine)

		#Try begin a session
		try:
			self.db_session = Session()
			self.db_session.begin()
		except Exception as e:
			raise e
		else:
			print(f"Database currently used: {self.get_database_path()}\n")

	def __del__(self):
		"""
		Description
		-----------
		Destroys a Db() object. It closes the active session.

		Raises
		-----------
		Raises an exception if we fail to close a session."""

		try:
			self.db_session.close()
		except Exception as e:
			raise Exception("Error: a problem occured while trying to disconnect from the database.")

	def get_database_path(self):
		"""
		Description
		-----------
		Returns the absolute path that leads to the database currently used """

		return self.database_path

	def has_unsaved_changes(self):
		"""
		Description
		-----------
		Should return True if there unsaved changes in the datafase and False otherwise."""

		return self.unsaved_changes_flag

	def save(self):
		pass
	
	def rollback(self):
		"""
		Description
		-----------
		If there are unsaved changes, it cancels them. Otherwise, it prints a warning message informing the user that there are no changes to cancel."""

		if not self.has_unsaved_changes():
			print("There are no unsaved changes to cancel.")
		else:
			#Try to rollback the unsaved changes
			try:
				self.db_session.rollback()
			except Exception as e:
				print("Error: a problem occured while trying to rollback changes from the database. In more detail:")
				print(e)
			else:
				#If rollback was successful, then there are no unsaved changes now.
				self.unsaved_changes_flag = False

	def clear(self):
		pass

	def dbinfo(self):
		pass

class NoDb:
	"""NoDb object is a object that provides the same interface as the Db object. It is used when we do NOT use a database in our application."""

	def __init__(self):
		"""
		Description
		-----------
		Initializes a Db() object.
		In more detail:
			-self.unused_database_message is a string: a message that will be displayed if the user attempts to use a method that can only be applied to a Db() object.
			-self.database_path is a string: None"""

		self.unused_database_message = "Error: You have to select a database to use before running this command. You can choose a database to use with the 'use' command\n"
		self.database_path = None

	def display_unused_warning(self):
		"""
		Description
		-----------
		Prints an error message informing us that the method we try to use applies only to Db() object."""

		print(self.unused_database_message)

	def get_database_path(self):
		"""
		Description
		-----------
		Returns the absolute path that leads to the database currently used."""

		return self.database_path

	def has_unsaved_changes(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def save(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""		

		self.display_unused_warning()

	def rollback(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""	

		self.display_unused_warning()

	def clear(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

	def dbinfo(self):
		"""
		Description
		-----------
		This method refer to commands that can only be applied when a database is used, so they print a relative warning message."""

		self.display_unused_warning()

def database_is_used(database_object):
	"""
	Description
	-----------
	Checks if a we currently use a database by checking the type of the database_object

	Parameters
	-----------
	database_is_used:
		An object (usually either a Db() object or a NoDb() object)

	Results
	-----------
	Returns True if the given object has type 'Db'. Otherwise it returns False."""
	
	if type(database_object).__name__ == 'Db':
		return True
	else:
		return False
