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

#TODO: Add two more scan codes (file scan failed, hash calculation failed)
#TODO: Write docstringss for everything
#TODO: add error message to the rollback function (everywhere)

class HashObject:
	def __init__(self,hash_func_name):

		self.hash_func = hash_func_name
		if self.hash_func == 'tlsh':
			self.obj = tlsh.Tlsh()
		elif self.hash_func == 'ssdeep':
			self.obj = ssdeep.Hash()
		else:
			self.obj = hashlib.new(name = self.hash_func)

	def get_hash(self):
		if self.hash_func == 'tlsh':
			self.obj.final()
			return self.obj.hexdigest()
		elif self.hash_func == 'ssdeep':
			return self.obj.digest(elimseq=False)
		else:
			return self.obj.hexdigest()
		
	def update(self,data):
		self.obj.update(data)


class ScanTarget:
	def __init__(self, path, origin, date_retrieved):
		self.full_path = path
		self.origin = origin
		self.date_retrieved = date_retrieved
	
	def __str__(self):
		return f"ScanTarget({self.full_path},{self.origin},{self.date_retrieved})"


class RemoteScanner:
	def __init__(self, arg):
		#Read the arg
		token_txt = arg['token_txt']
		platform = arg['platform']
		token_term = arg['token-term']

		#If there is a file which contains the token, scan it to obtain the token.
		#Otherwise, prompt the user enter the token
		if isfile(token_txt):
			with open(token_txt, 'r', encoding='utf-8') as f:
				token = f.readline()
				if token[-1] == '\n':
					token = token[:-1] #delete \n from the token by hand
		else:
			print("You can still access public repositories without using authentication. Just leave the following prompt empty!")
			token = input(f"{platform} {token_term}:")

		self.token = token
		self.term = arg['term']
		self.dir_type = arg['dir_type']

	def download_targets(self, target_list, download_location_parameter, recursion_flag_parameter):
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

		#attempt to create a folder at the download destination, where the repo's contents will be saved
		try:
			mkdir(repo_folder)
		except Exception as e:
			print(f"Error: something went wrong while creating the folder {repo_folder}. In more detail:")
			print(e)
			return []
		else:
			scan_target_objects_list = []
			for branch in self.get_repo_branches(repo):
				branch_name = self.get_branch_name(branch)
				branch_folder_path = join(repo_folder, branch_name)
				try:
					#create a folder with the branch's name and save
					mkdir(branch_folder_path)
				except Exception as e:
					print(f"Error: something went wrong while creating the folder {branch_folder_path}. In more detail:")
					print(e)
				else:
					print(f"Downloading branch {branch_name}")
					#download the root directory of the branch
					ref = self.get_branch_ref(branch)
					new_scan_targets = self.download_remote_directory(repo, ref, "", branch_folder_path, recursion_flag_parameter)
					scan_target_objects_list.extend(new_scan_targets)

			return scan_target_objects_list

	def download_remote_directory(self, repo, ref, path, download_destination, recursion_flag_parameter):
		#https://sookocheff.com/post/tools/downloading-directories-of-code-from-github-using-the-github-api/

		#get the contents of the directory you wish to download
		contents = self.get_directory_contents(repo, path, ref)
		#iterate through the files inside the directory you wish to download
		scan_target_objects_list = []

		for content in contents:
			content_name = self.get_content_name(content)
			content_path = self.get_content_path(content)
			content_type = self.get_content_type(content)

			if content_type == self.dir_type:
				if not recursion_flag_parameter:
					continue

				#If the file is a directory, create an equivelant folder in your system
				#path of equivelant folder == download_location + path inside the folder + the name of the current file
				mkdir(join(download_destination,path,content_name))
				#download the contents of the directory inside the folder you just created
				new_scan_targets = self.download_remote_directory(repo, ref, content_path, download_destination, recursion_flag_parameter)
				scan_target_objects_list.extend(new_scan_targets)
			else:
				#If the file is a single file, get its contents and write them inside a new file inside the equivelant folder
				try:
					print(f"Downloading {join(path,content_name)}...")
					new_file_path = join(download_destination,path,content_name)

					file_content = self.get_file(repo, content_path, ref)
					file_data = b64decode(self.get_file_data(file_content))
					file_out = open(new_file_path, "wb+") #wb+ in order to write bytes
					file_out.write(file_data)
					file_out.close()

					scan_target_objects_list.extend([ScanTarget(new_file_path, self.get_file_url(file_content, repo), datetime.now())])
				except Exception as e:
					print(f"Error:downloading {content_path} failed. In more detail:")
					print(e)

		return scan_target_objects_list

	def name_of_repo_folder(self, repo_name, download_location_parameter):
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
	def __init__(self):
		github_parameters = {
		"platform": "Github",
		"token_txt": "github-token.txt",
		"term": "repo",
		"dir_type": 'dir',
		"token-term": "personal access token"
		}

		super(GithubScanner, self).__init__(github_parameters)
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
		return repo_object.get_dir_contents(path, ref= sha)

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
	def __init__(self):
		gitlab_parameters = {
		"platform": "Gitlab",
		"token_txt": "gitlab-token.txt",
		"term": "project",
		"dir_type": 'tree',
		"token-term": "personal access token"
		}

		super(GitlabScanner, self).__init__(gitlab_parameters)
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
		return 'https://gitlab.com/api/v4/projects/' + str(project_object.attributes['id']) + '/repository/blobs/' + file_object.blob_id + '/raw'

	def get_file_data(self, file_object):
		return file_object.content

	def get_file(self, project_object, path_param, ref_param):
		return project_object.files.get(file_path = path_param, ref = ref_param)


def format_local_targets(target_list, hostname_parameter, recursion_flag_parameter):

	scan_target_objects_list = []

	for target in target_list:
		if not exists(target):
			print(f"Error: No such file or directory: {target}")
		elif isfile(target):
			scan_target_objects_list.append(ScanTarget(abspath(target),hostname_parameter,datetime.now()))
		elif recursion_flag_parameter:
			for root, dirs, files in walk(abspath(target)):
				for file in files:
					target_path = join(root, file)
					scan_target_objects_list.append(ScanTarget(target_path,hostname_parameter,datetime.now()))
		else:
			for file in listdir(target):
				target_path = abspath(join(target, file))
				if isfile(target_path):
					scan_target_objects_list.append(ScanTarget(target_path,hostname_parameter,datetime.now()))

	return scan_target_objects_list


def scanner(db_session_param, scan_targets_parameter, hash_functions_parameter, download_location_parameter, scan_id_parameter, recursion_flag_parameter = True):

	#Scan local targets. List of ScanTargets (skip if invalid)
	if scan_targets_parameter[0]:
		local_targets = format_local_targets(scan_targets_parameter[0], gethostname(), recursion_flag_parameter)
		scan_local(db_session_param, local_targets, hash_functions_parameter, scan_id_parameter)

	#Download Github targets locally. List of ScanTargets (skip if invalid)
	if scan_targets_parameter[1]:
		github_targets = GithubScanner().download_targets(scan_targets_parameter[1], download_location_parameter, recursion_flag_parameter)
		scan_local(db_session_param, github_targets, hash_functions_parameter, scan_id_parameter)

	#Download Gitlab targets locally. List of ScanTargets (skip if invalid)
	if scan_targets_parameter[2]:
		gitlab_targets = GitlabScanner().download_targets(scan_targets_parameter[2], download_location_parameter, recursion_flag_parameter) 
		scan_local(db_session_param, gitlab_targets, hash_functions_parameter, scan_id_parameter)

	scan_result = 0 #TODO: fix this
	return scan_result

def scan_local(db_session_param, scan_target_objects_list, hash_functions_parameter, scan_id_parameter):
	for t in scan_target_objects_list:
		try:
			new_file_id = insert_file(db_session_param, t, scan_id_parameter)
		except Exception as e:
			print(f"Error: something went wrong while scanning file {t.full_path}. In more detail:")
			print(e)
		else:
			print(f"Calculating hashes for {t.full_path}...")

			try:
				insert_swhid(db_session_param, t.full_path, new_file_id)
			except Exception as e:
				print(f"Error: something went wrong while calculating swhid hash for file {t.full_path}. In more detail:")
				print(e)		

			if hash_functions_parameter:
				for hash_func in hash_functions_parameter:
					try:
						insert_hash(db_session_param, t.full_path, hash_func, new_file_id)
					except Exception as e:
						print(f"Error: something went wrong while calculating {hash_func} hash for file {t.full_path}. In more detail:")
						print(e)			

def insert_file(db_session_param, target_object, scan_id_parameter):

	#obtain all the necessary file information
	file_info = stat(target_object.full_path)
	file_info = {
		"scan_id": scan_id_parameter,
		"file_path": target_object.full_path,
		"file_name": basename(target_object.full_path),
		"file_extension": splitext(target_object.full_path)[1],
		"file_size": getsize(target_object.full_path),
		"date_created": datetime.fromtimestamp(file_info.st_ctime),
		"date_modified": datetime.fromtimestamp(file_info.st_mtime),
		"date_retrieved": target_object.date_retrieved,
		"swh_known": None,
		"updated": True,
		"origin": target_object.origin,
	}
	
	#construct file object
	f = File(**file_info)

	#check for others with the same attrs and make them updated = False
	possible_duplicates_fetch = db_session_param.query(File).filter(File.file_path == target_object.full_path, File.origin == target_object.origin, File.updated.is_(True))
	if bool(possible_duplicates_fetch.first()):
		for possible_duplicates in possible_duplicates_fetch.all():
			possible_duplicates.updated = False

	#insert File in the database
	try:
		db_session_param.add(f)
	except Exception as e:
		raise e
	else:
		db_session_param.flush()
		return f.id

def insert_hash(db_session_param, target_object_path, hash_func_name, file_id_parameter):

	#block size
	chunk_size = 4096

	#calculate hash
	hash_object = HashObject(hash_func_name)
		
	try:
		f = open(target_object_path, 'rb') #rb = open in binary format
	except Exception as e:
		raise e
	else:
		for block in iter(lambda: f.read(chunk_size), b""):
			hash_object.update(block)

	#construct hash object
	h = Hash(hash_value = hash_object.get_hash(), hash_function_name = hash_func_name, file_id = file_id_parameter)

	#insert Hash in the database
	try:
		db_session_param.add(h)
	except Exception as e:
		raise e
	else:
		db_session_param.flush()
		#TODO: return something

def insert_swhid(db_session_param, target_object_path, file_id_parameter):

	#calculate SWHID
	try:
		swh_identifier = pid_of_file(target_object_path)
	except Exception as e:
		raise e
		return False

	#insert Hash in the database
	try:
		#construct hash object and add it
		h = Hash(hash_value = swh_identifier, hash_function_name = 'swhid', file_id = file_id_parameter)
		db_session_param.add(h)
	except Exception as e:
		raise e
		return False
	else:
		x = db_session_param.query(File).get(file_id_parameter)
		x.swh_known = resolve_swhid(swh_identifier)
		db_session_param.flush()

def resolve_swhid(swhid_hash):
	api_url = 'https://archive.softwareheritage.org/api/1/resolve/' + swhid_hash + '/'
	r = requests.get(api_url)

	if r.status_code == 200:
		return True
	elif r.status_code == 404:
		return False
	else:
		return None