import hashlib
import xxhash
from datetime import datetime
from os import mkdir, listdir, walk, stat
from os.path import isdir, isfile, join, exists, abspath, basename, splitext, getsize
from base64 import b64decode
from github import Github
import gitlab
from socket import gethostname
from table_classes import *
import ssdeep
import tlsh
from swh.model.cli import pid_of_file
import requests
#Note: swh.model requires to run 'pip install dulwich' manually. Do not forget to inculde 'dulwich' in the requirements.txt

class HashObject:
	"""
	This class is an abstraction of the hash objects the built-in hahslib library provides.
	We use this class in order to provide a common interface for all the hash functions supported by hashesdb,
	since some python libraries that implement fuzzy hash functions use different names for equivelant methods.
	"""

	def __init__(self,hash_func_name):
		"""
		Description
		-----------
		Initilalizes a HashObject according to the hash function name.
		Stores the hash function name and an object which is constructed using the appropriate constructor of the library that implements the given hash function.
		
		Parameters
		-----------
		hash_func_name - string
			The name of the hash function from which the hash will be produced.
		"""
		
		self.hash_func = hash_func_name
		if self.hash_func == 'tlsh':
			self.obj = tlsh.Tlsh()
		elif self.hash_func == 'ssdeep':
			self.obj = ssdeep.Hash()
		elif self.hash_func == 'xxh32':
			self.obj = xxhash.xxh32()
		elif self.hash_func == 'xxh64':
			self.obj = xxhash.xxh64()
		else:
			self.obj = hashlib.new(name = self.hash_func)

	def get_hash(self):
		"""
		Description
		-----------
		Returns the hex digest of the hash through the use of the appropriate method of the library that implements the given hash function.
		"""

		if self.hash_func == 'tlsh':
			self.obj.final()
			return self.obj.hexdigest()
		elif self.hash_func == 'ssdeep':
			return self.obj.digest(elimseq=False)
		elif self.hash_func == 'shake_128':
			return self.obj.hexdigest(128)
		elif self.hash_func == 'shake_256':
			return self.obj.hexdigest(256)
		else:
			return self.obj.hexdigest()
		
	def update(self,data):
		"""
		Description
		-----------
		Equivelant to the hash.update() method of the object.
		https://docs.python.org/3/library/hashlib.html#hashlib.hash.update
		"""
		
		self.obj.update(data)


class ScanTarget:
	"""
	This class stores scannning information about local targets that will be inserted into the database.
	These information are the following:
		-full_path: this variable specifies from where the target was located when scanned
		-origin: this variable specifies where the file was found.
			If the file was downloaded from a remote location, a URL from which the raw file can be retrived is saved. 
			Otherwise, if the file was a local target, the hostname of the machine is saved.
	"""

	def __init__(self, path, origin, date_retrieved):
		self.full_path = path
		self.origin = origin
		self.date_retrieved = date_retrieved
	
	def __str__(self):	
		return f"ScanTarget({self.full_path},{self.origin},{self.date_retrieved})"


class RemoteScanner:
	"""
	This is an abstract class that allows scanning of remote files.
	This class uses methods that are not implemented by the RemoteScanner class.
	These methods use API calls and should be implemented independently by each class that inherits this class.
	"""

	def __init__(self, arg):
		"""
		Description
		-----------
		Initilalizes a RemoteScanner. This initilizer is supposed to be called by a class that inherits this class.

		Parameters
		-----------
		arg - dictionary
			A dictionary that contains information about the platform in which the targets are stored.
		"""

		#Read the arg
		token_txt = arg['token_txt']
		platform = arg['platform']
		token_term = arg['token-term']

		#If there is a file which contains the token, scan it to obtain the token.
		if isfile(token_txt):
			with open(token_txt, 'r', encoding='utf-8') as f:
				token = f.readline()
				if token[-1] == '\n':
					token = token[:-1] #delete \n from the token by hand
		#Otherwise, prompt the user enter the token
		else:
			print("You can still access public repositories without using authentication. Just leave the following prompt empty!")
			token = input(f"{platform} {token_term}:")

		self.token = token
		self.term = arg['term']
		self.dir_type = arg['dir_type']

	def download_targets(self, target_list, download_location_parameter, recursion_flag_parameter):
		"""
		Description
		-----------
		Downloads the scan targets, saves them at the specified location and returns a list of ScanTargets to be scanned.

		Parameters
		-----------
		target_list - List of targets
			A list of repos/projects that are targets for scanning

		download_location_parameter - string
			A path(relative or absolute) to the location in which the downloaded files will be saved.

		recursion_flag_parameter: boolean, optional
			Default value: True
			If this parameter is True, then we recursively scan the contents of all the directories.
			Otherwise we do not scan the directories (we skip them).

		Returns
		-----------
		scan_target_objects_list - list of ScanTargets
			A list of ScanTargets. Each ScanTarget corresponds to a local target, whose origin is a remote URL.
		"""

		#If there are no targets to scan, return an empty list
		if not target_list:
			return []

		#List with the paths of the repos I downloaded
		scan_target_objects_list = []

		#Download each repo and add it to the results list
		for repo in target_list:
			new_scan_targets = self.download_repo(repo, download_location_parameter, recursion_flag_parameter)
			scan_target_objects_list.extend(new_scan_targets)

		return scan_target_objects_list

	def download_repo(self, repo_parameter, download_location_parameter, recursion_flag_parameter):
		"""
		Description
		-----------
		Downloads the scan targets, saves them at the specified location and returns a list of ScanTargets to be scanned.

		Parameters
		-----------
		repo_parameter - string
			Name/id of the repo that will be downloaded

		download_location_parameter - string
			A path(relative or absolute) to the location in which the downloaded files will be saved.

		recursion_flag_parameter: boolean, optional
			Default value: True
			If this parameter is True, then we recursively scan the contents of all the directories.
			Otherwise we do not scan the directories (we skip them).

		Returns
		-----------
		scan_target_objects_list - list of ScanTargets
			A list of ScanTargets. Each ScanTarget corresponds to a local target, whose origin is a remote URL.
		"""

		#Attempt to get the repo
		try:
			repo = self.get_repo(repo_parameter)
		except Exception as e:
			print(f"Error: Downloading {self.term} {repo_parameter} failed. In more detail:")
			print(e)
			return []

		repo_name = self.get_repo_name(repo)
		repo_folder = self.name_of_repo_folder(repo_name, download_location_parameter)
		print(f"Downloading {repo_name}")

		#Attempt to create a folder at the download destination, where the repo's contents will be saved
		try:
			mkdir(repo_folder)
		except Exception as e:
			#If you fail to create a folder, print an error message and return an empty list
			print(f"Error: something went wrong while creating the folder {repo_folder}. In more detail:")
			print(e)
			return []
		else:
			#The list of ScanTargets that will be filled with ScanTarget objects to be scanned
			scan_target_objects_list = []
			#For each branch, create a subfolder (in which the branch's content will be saved) and download the branch's content inside the subfolder
			for branch in self.get_repo_branches(repo):
				branch_name = self.get_branch_name(branch)
				branch_folder_path = join(repo_folder, branch_name)
				try:
					#Create a folder with the branch's name and save
					mkdir(branch_folder_path)
				except Exception as e:
					print(f"Error: something went wrong while creating the folder {branch_folder_path}. In more detail:")
					print(e)
				else:
					print(f"Downloading branch {branch_name}")
					ref = self.get_branch_ref(branch) #get something that identifies the branch you want to download
					#Download the contents of the branch's root directory (recursively or not) and add the returned ScanTargets to the list that will be returned at the end
					new_scan_targets = self.download_remote_directory(repo, ref, "", branch_folder_path, recursion_flag_parameter)
					scan_target_objects_list.extend(new_scan_targets)

			return scan_target_objects_list

	def download_remote_directory(self, repo, ref, path, download_destination, recursion_flag_parameter):
		"""
		Description
		-----------
		Downloads the contents of a remote directory, saves them at the specified location and returns a list of ScanTargets to be scanned.

		Parameters
		-----------
		repo_parameter - string
			Name/id of the repo that will be downloaded

		ref - string
			A reference to a specific branch

		path - string
			The path of the directory/file to be scanned. Paths are relative and do not contain info about the repo or the branch.

		download_location_parameter - string
			A path(relative or absolute) to the location in which the downloaded files will be saved.

		recursion_flag_parameter: boolean, optional
			Default value: True
			If this parameter is True, then we recursively scan the contents of all the directories.
			Otherwise we do not scan the directories (we skip them).

		Returns
		-----------
		scan_target_objects_list - list of ScanTargets
			A list of ScanTargets. Each ScanTarget corresponds to a local target, whose origin is a remote URL.
		"""

		#get the contents of the directory you wish to download
		contents = self.get_directory_contents(repo, path, ref)
		
		#The list of ScanTargets that will be filled with ScanTarget objects to be scanned
		scan_target_objects_list = []

		#iterate through the files inside the directory you wish to download
		for content in contents:
			content_name = self.get_content_name(content)
			content_path = self.get_content_path(content)
			content_type = self.get_content_type(content)

			if content_type == self.dir_type:
				#If the file is a directory and you do NOT want to scan it recursively, then skip it
				if not recursion_flag_parameter:
					continue

				#If the file is a directory and you want to scan it recursively, create an equivelant folder in your system
				#path of equivelant folder == download_location + path inside the folder + the name of the current file
				mkdir(join(download_destination,path,content_name))
				#download the contents of the directory inside the folder you just created (all parameters remain the same except of the path parameter)
				new_scan_targets = self.download_remote_directory(repo, ref, content_path, download_destination, recursion_flag_parameter)
				scan_target_objects_list.extend(new_scan_targets)
			else:
				#If the file is a single file, get its contents and write them inside a new file inside the equivelant folder
				try:
					print(f"Downloading {join(path,content_name)}...")
					#path of new file = download destination + path inside repo + name of the file
					new_file_path = join(download_destination,path,content_name)

					#Write the contents of the remote file to a local file
					file_content = self.get_file(repo, content_path, ref)
					file_data = b64decode(self.get_file_data(file_content)) #decode the content
					file_out = open(new_file_path, "wb+") #wb+ in order to write bytes
					file_out.write(file_data)
					file_out.close()
					
					#Add the returned ScanTargets to the list that will be returned at the end
					scan_target_objects_list.extend([ScanTarget(new_file_path, self.get_file_url(file_content, repo), datetime.now())])
				except Exception as e:
					print(f"Error:downloading {content_path} failed. In more detail:")
					print(e)

		return scan_target_objects_list

	def name_of_repo_folder(self, repo_name, download_location_parameter):
		"""
		Description
		-----------
		Finds a name that is not already taken  for the folder in which the contents of a repo/project will be stored. 
		For example, for the repo 'user/test_repo', it will try 'test_repo', 'test_repo(1)', 'test_repo(2)',... etc until it finds name that is not already taken by other files.

		Parameters
		-----------
		repo_name - string
			The name of the repository/project you want to save inside the folder

		download_location_parameter - string
			A path(relative or absolute) to the location in which the downloaded files will be saved.

		Returns
		-----------
		repo_folder_path - string
			The name of the folder that will be created.
		"""

		#path at which we intend to save the new repo == at a new folder with the repo's name inside the download destination
		new_folder_path = join(download_location_parameter, repo_name)

		#if a folder with the repo's name already exists at the download destination, try to rename it ('example name (1)','example name (2)',...)
		copy_number = 0
		repo_folder_path = new_folder_path

		#find the minimum number i such that 'example name (i)' does not already exists 
		while exists(repo_folder_path):
			copy_number += 1
			repo_folder_path = new_folder_path + "(" + str(copy_number) + ")"

		return repo_folder_path


class GithubScanner(RemoteScanner):
	"""
	This class implements the RemoteScanner class. It makes it possible to scan Github repositories through the Github API.
	PyGithub documentation: https://pygithub.readthedocs.io/en/latest/introduction.html
	"""

	def __init__(self):
		github_parameters = {
		"platform": "Github",
		"token_txt": "github-token.txt",
		"term": "repo",
		"dir_type": 'dir',
		"token-term": "personal access token"
		}

		super(GithubScanner, self).__init__(github_parameters) #RemoteScanner.__init__()
		self.g = Github(self.token)

	def get_repo(self, repo_parameter):
		return self.g.get_repo(repo_parameter)

	def get_repo_name(self, repo_object):
		return repo_object.name

	def get_repo_branches(self, repo_object):
		return repo_object.get_branches()

	def get_branch_name(self, branch_object):
		return branch_object.name

	def get_branch_ref(self, branch_object):
		return branch_object.commit.sha

	def get_directory_contents(self, repo_object, path, sha):
		return repo_object.get_contents(path, ref= sha)

	def get_content_name(self, content_object):
		return content_object.name

	def get_content_type(self, content_object):
		return content_object.type

	def get_content_path(self, content_object):
		return content_object.path

	def get_file_url(self, file_object, repo_object):
		#repo object is useless in this function but it is needed at th Gitlab().get_file_url
		return file_object.download_url

	def get_file_data(self, file_object):
		return file_object.content

	def get_file(self, repo_object, path_param, ref_param):
		return repo_object.get_contents(path_param, ref=ref_param)


class GitlabScanner(RemoteScanner):
	"""
	This class implements the RemoteScanner class. It makes it possible to scan Gitlab projects through the Gitlab API.
	python-gitlab documentation: https://python-gitlab.readthedocs.io/en/stable/
	"""

	def __init__(self):
		gitlab_parameters = {
		"platform": "Gitlab",
		"token_txt": "gitlab-token.txt",
		"term": "project",
		"dir_type": 'tree',
		"token-term": "personal access token"
		}

		super(GitlabScanner, self).__init__(gitlab_parameters) #RemoteScanner.__init__()
		self.g = gitlab.Gitlab('https://gitlab.com/',private_token = self.token)

	def get_repo(self, project_parameter):
		return self.g.projects.get(project_parameter)

	def get_repo_name(self, project_object):
		return project_object.attributes['name']

	def get_repo_branches(self, project_object):
		return project_object.branches.list()

	def get_branch_name(self, branch_object):
		return branch_object.attributes['name']

	def get_branch_ref(self, branch_object):
		return self.get_branch_name(branch_object)

	def get_directory_contents(self, project_object, path, branch_name):
		return project_object.repository_tree(path = path, ref = branch_name)

	def get_content_name(self, content_object):
		return content_object['name']

	def get_content_type(self, content_object):
		return content_object['type']

	def get_content_path(self, content_object):
		return content_object['path']

	def get_file_url(self, file_object, project_object):
		#Gitlab API documentation page: https://docs.gitlab.com/ee/api/repositories.html#raw-blob-content
		return 'https://gitlab.com/api/v4/projects/' + str(project_object.attributes['id']) + '/repository/blobs/' + file_object.blob_id + '/raw'

	def get_file_data(self, file_object):
		return file_object.content

	def get_file(self, project_object, path_param, ref_param):
		return project_object.files.get(file_path = path_param, ref = ref_param)


def format_local_targets(target_list, hostname_parameter, recursion_flag_parameter):
	"""
	Description
	-----------
	Receives a list of local targets as input and produces a list of equivelant ScanTarget objects as output. 

	Parameters
	-----------
	target_list - list of paths 
		List of paths to local targets that we want to scan.

	hostname_parameter - string
		The hostname of the machine were the local targets are located.

	recursion_flag_parameter: boolean, optional
		Default value: True
		If this parameter is True, then we recursively scan the contents of all the directories.
		Otherwise we do not scan the directories (we skip them).

	Returns
	-----------
	scan_target_objects_list - list of ScanTargets
		A list of ScanTargets. Each ScanTarget corresponds to a local target given as input to the scan command.
	"""

	#All the local ScanTargets will have the hostname_parameter as origin. The path of all ScanTargets will be absolute paths 

	#The list of ScanTargets that will be returned
	scan_target_objects_list = []

	#For each target in the target list:
	for target in target_list:
		#If the target does not exist, print an erroor message
		if not exists(target):
			print(f"Error: No such file or directory: {target}")
		#If the target is a file, construct the equivelant ScanTarget and append it to the list that will be returned
		elif isfile(target):
			scan_target_objects_list.append(ScanTarget(abspath(target),hostname_parameter,datetime.now()))
		#Else,if the file is a directory AND we want to scan it recursively, then scan all the files inside it(using os.walk)
		elif recursion_flag_parameter:
			for root, dirs, files in walk(abspath(target)):
				for file in files:
					target_path = join(root, file)
					#Construct the equivelant ScanTarget and append it to the list that will be returned
					scan_target_objects_list.append(ScanTarget(target_path,hostname_parameter,datetime.now()))
		#Else,if the file is a directory AND we do NOT want to scan it recursively, then scan only the files immediatly inside it(using os.listdir)
		else:
			for file in listdir(target):
				target_path = abspath(join(target, file))
				if isfile(target_path):
					#Construct the equivelant ScanTarget and append it to the list that will be returned
					scan_target_objects_list.append(ScanTarget(target_path,hostname_parameter,datetime.now()))

	return scan_target_objects_list

def scanner(db_session_param, scan_targets_parameter, hash_functions_parameter, download_location_parameter, scan_id_parameter, recursion_flag_parameter = True):
	"""
	Description
	-----------
	Scan local targets, github repos and gitlab projects.

	Parameters
	-----------
	db_session_param - SQLAlchemy session object
		An active session from which we apply changes to the database

	scan_targets_parameter: a list of lists of scan targets(strings)
		List 1: a list of local scan targets (files and directories)
		List 2: a list of Github repos
		List 3: a list of Gitlab project ids

	hash_functions_parameter - list of strings
		A list of hash function names. For each hash function in the list, the hash value of the file will be calculated and inserted into the database.

	download_location_parameter: string
		A path(relative or absolute) to the location in which the downloaded files will be saved.
		The only files we download are remote scan targets(links to github/gitlab)

	scan_id_parameter - int
		The unique id of the scan during which we scan this particular file (primary key of SCAN table)

	recursion_flag_parameter: boolean, optional
		Default value: True
		If this parameter is True, then we recursively scan the contents of all the directories.
		Otherwise we do not scan the directories (we skip them).

	Returns
	-----------
	scan_result - int
		The scan code that describes the result of the scan
	"""

	scan_result = 0

	#In the following lines, we reset the scan_code variable using the max() function, since we want to return the most important error(= greater error code)

	#Scan local targets.
	if scan_targets_parameter[0]:
		local_targets = format_local_targets(scan_targets_parameter[0], gethostname(), recursion_flag_parameter) #List of ScanTargets
		scan_result = max(scan_result, scan_local(db_session_param, local_targets, hash_functions_parameter, scan_id_parameter)) 

	#Download Github targets locally and scan them.
	if scan_targets_parameter[1]:
		github_targets = GithubScanner().download_targets(scan_targets_parameter[1], download_location_parameter, recursion_flag_parameter) #List of ScanTargets
		scan_result = max(scan_result, scan_local(db_session_param, github_targets, hash_functions_parameter, scan_id_parameter))

	#Download Gitlab targets locally and scan them.
	if scan_targets_parameter[2]:
		gitlab_targets = GitlabScanner().download_targets(scan_targets_parameter[2], download_location_parameter, recursion_flag_parameter) #List of ScanTargets
		scan_result = max(scan_result, scan_local(db_session_param, gitlab_targets, hash_functions_parameter, scan_id_parameter))

	return scan_result

def scan_local(db_session_param, scan_target_objects_list, hash_functions_parameter, scan_id_parameter):
	"""
	Description
	-----------
	Scan local targets: Insert File records for each of them and then calculate 

	Parameters
	-----------
	db_session_param - SQLAlchemy session object
		An active session from which we apply changes to the database

	scan_target_objects_list - list of ScanTargets
		A list of ScanTarget objects that will be scanned

	hash_functions_parameter - list of strings
		A list of hash function names. For each hash function in the list, the hash value of the file will be calculated and inserted into the database.

	scan_id_parameter - int
		The unique id of the scan during which we scan this particular file (primary key of SCAN table)

	Returns
	-----------
	scan_code_of_scan - int
		The scan code that describes the outcome of the scan (primary key of SCAN_CODE table).
	"""

	#Flags according to which we decide which scan code to return
	all_files_scanned = True
	all_hashes_calculated = True

	for t in scan_target_objects_list:
		#For every ScanTarget object, insert a File record to the FILE table
		try:
			new_file_id = insert_file(db_session_param, t, scan_id_parameter)
		except Exception as e:
			#If the insertion of the File fails, then change the relative flag
			all_files_scanned = False
			print(f"Error: something went wrong while scanning file {t.full_path}. In more detail:")
			print(e)
		else:
			#If the insertion of the File is successful
			print(f"Calculating hashes for {t.full_path}...")

			#Calculate the SWHID and insert it into the database
			try:
				insert_swhid(db_session_param, t.full_path, new_file_id)
			except Exception as e:
				all_hashes_calculated = False
				print(f"Error: something went wrong while calculating swhid hash for file {t.full_path}. In more detail:")
				print(e)		

			#Calculate the rest of the hashes using the hash functions given as input
			if hash_functions_parameter:
				#For every hash function, calculate the hash value of the file and insert it into the database
				for hash_func in hash_functions_parameter:
					try:
						insert_hash(db_session_param, t.full_path, hash_func, new_file_id)
					except Exception as e:
						#If the insertion of the Hash fails, then change the relative flag
						all_hashes_calculated = False
						print(f"Error: something went wrong while calculating {hash_func} hash for file {t.full_path}. In more detail:")
						print(e)


	#Return the scan code according to the flags
	if not all_files_scanned:
		scan_code_of_scan = 4
	elif not all_hashes_calculated:
		scan_code_of_scan = 3
	else:
		scan_code_of_scan = 0

	return scan_code_of_scan	

def insert_file(db_session_param, target_object, scan_id_parameter):
	"""
	Description
	-----------
	Insert a new FILE record in the database

	Parameters
	-----------
	db_session_param - SQLAlchemy session object
		An active session from which we apply changes to the database

	target_object_path - string
		Path to the file for which we calculate the hash value

	scan_id_parameter - int
		The unique id of the scan during which we scan this particular file (primary key of SCAN table)

	Returns
	-----------
	f.id - int
		The unique id of the File record we just added.

	Raises
	-----------
	Raises an Exception:
		-if the insertion of the File into the database fails
	"""

	#obtain all the necessary file information for the FILE record and store them inside a dictionary
	#the id of the FILE record will be given automatically by SQLAlchemy when we try to add the File object to the database
	file_stat = stat(target_object.full_path)
	file_info = {
		"scan_id": scan_id_parameter,
		"file_path": target_object.full_path,
		"file_name": basename(target_object.full_path),
		"file_extension": splitext(target_object.full_path)[1],
		"file_size": getsize(target_object.full_path),
		"date_created": datetime.fromtimestamp(file_stat.st_ctime),
		"date_modified": datetime.fromtimestamp(file_stat.st_mtime),
		"date_retrieved": target_object.date_retrieved,
		"swh_known": None,
		"updated": True,
		"origin": target_object.origin,
	}
	
	#Construct file object
	f = File(**file_info)

	#Check for others with the exact same attributes (saved in the same location and came from the same origin) and mark them as 'NOT UPDATED'
	possible_duplicates_fetch = db_session_param.query(File).filter(File.file_path == target_object.full_path, File.origin == target_object.origin, File.updated.is_(True))
	if bool(possible_duplicates_fetch.first()):
		for possible_duplicates in possible_duplicates_fetch.all():
			possible_duplicates.updated = False

	#Insert File in the database and return the id it got
	try:
		db_session_param.add(f)
	except Exception as e:
		raise e
	else:
		db_session_param.flush()
		return f.id

def insert_hash(db_session_param, target_object_path, hash_func_name, file_id_parameter):
	"""
	Description
	-----------
	Calculate the hash of a given file and insert it into the database

	Parameters
	-----------
	db_session_param - SQLAlchemy session object
		An active session from which we apply changes to the database

	target_object_path - string
		Path to the file for which we calculate the hash value

	hash_func_name - string
		The name of the hash function which will be used to calculate the hash value

	file_id_parameter - int
		The unique id of the file for which we calculate the SWHID (primary key of FILE table)

	Raises
	-----------
	Raises an Exception:
		-if the calculation of the hash fails
		-if the insertion of the hash into the database fails
	"""


	#Block size (the hash calculation is done one memory block at a time, in order to be able to calculate hashes of files that exceed the size of the memory)
	chunk_size = 4096

	#Construct a HashObject 
	hash_object = HashObject(hash_func_name)

	#Construct hash value using the interface provided by the HashObject class		
	try:
		f = open(target_object_path, 'rb') #rb = open in binary format
	except Exception as e:
		raise e
	else:
		for block in iter(lambda: f.read(chunk_size), b""):
			hash_object.update(block)

		#Close the file
		f.close()

	#Construct Hash object
	h = Hash(hash_value = hash_object.get_hash(), hash_function_name = hash_func_name, file_id = file_id_parameter)

	#Insert Hash in the database
	try:
		db_session_param.add(h)
	except Exception as e:
		raise e
	else:
		db_session_param.flush()

def insert_swhid(db_session_param, target_object_path, file_id_parameter):
	"""
	Description
	-----------
	Calculate the SWHID of a given file, insert it into the database and update the 'swh-known' column of the file

	Parameters
	-----------
	db_session_param - SQLAlchemy session object
		An active session from which we apply changes to the database

	target_object_path - string
		Path to the file for which we calculate the SWHID

	file_id_parameter - int
		The unique id of the file for which we calculate the SWHID (primary key of FILE table)

	Raises
	-----------
	Raises an Exception:
		-if the calculation of the SWHID fails
		-if the insertion of the SHWID Hash object into the database fails
	"""

	#Calculate SWHID
	try:
		swh_identifier = pid_of_file(target_object_path) #function imported from swh.model.cli
	except Exception as e:
		raise e
		return False

	#Insert SWHID in the database
	try:
		#construct hash object and try to add it
		h = Hash(hash_value = swh_identifier, hash_function_name = 'swhid', file_id = file_id_parameter)
		db_session_param.add(h)
	except Exception as e:
		#if you fail, raise an Exception
		raise e
		return False
	else:
		#Update the 'swh_known' column of the file, after searching for it in the SoftwareHeritage archive usine resolve_swhid
		x = db_session_param.query(File).get(file_id_parameter)
		x.swh_known = resolve_swhid(swh_identifier)
		db_session_param.flush()

def resolve_swhid(swhid_hash):
	"""
	Description
	-----------
	Checks if a SWHID is stored in the SoftwareHeritage API

	Parameters
	-----------
	swhid_hash - swh.model.identifiers.CoreSWHID
		The output of a call to pid_of_file. Contains the SWHID hash.

	Results
	-----------
	This functions returns:
		-True, if the SWHID exists in the SoftwareHeritage archive
		-False, if the SWHID does NOT exist in the SoftwareHeritage archive
		-None, if something went wrong
	"""

	#SoftwareHeritage API documentation:
	#https://docs.softwareheritage.org/devel/apidoc/swh.web.api.views.identifiers.html#swh.web.api.views.identifiers.api_resolve_swhid
	api_url = 'https://archive.softwareheritage.org/api/1/resolve/' + swhid_hash + '/'
	
	#GET request
	r = requests.get(api_url)

	if r.status_code == 200:
		return True
	elif r.status_code == 404:
		return False
	else:
		return None