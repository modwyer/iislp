import os, sys, configparser, datetime
from scripts.exceptions import ArgumentError
from enum import Enum

class ConfigKeys(Enum):
	last_updated 	= 0		#Last update datetime for config file.
	iis_logs 		= 1		#Dir containing iis log files for parsing.
	csv 			= 2		#Dir containing CSV files generated by iislp during execution.
	bulk 			= 3		#Create 100k+ row CSV files, using multiple log files.
	bulk_csv 		= 4		#Dir containing CSV files containing 100k+ rows.
	app 			= 5		#Dir containing the IIS Log Parser (iislp) application.
	logging 		= 6		#Dir containing log files generated from iislp app during execution.
	csv_stor 		= 7		#Dir containing CSV files to be uploaded to the database.	
	log_done 		= 8		#Dir containing all the IIS Log files.
	file_mover 	= 9		#Path to the file_mover.py file.
	temp 		= 10 	#Path to a temp directory for use during execution.
	bulk_logs		= 11		#Path to log files to process for bulk processing.
	bulk_csv_max 	= 12		#Record count limit.  (Eg. If CSV count > bulk_csv_max, save CSV as a back-up copy)
	logsdone_log	= 13		#Path of the file that keeps track of what logs have been processed.
	runtime_log	= 14		#Path of the log file written to during execution.

class ConfigMgr(object):
	def __init__(self):
		self.dir = os.path.dirname(os.path.abspath(__file__))
		#self.config_path = os.path.abspath(os.path.join(self.dir, '..', '..', '..' '\\config\\settings.ini'))		
		self.config_path = os.path.abspath(os.path.join(self.dir, '..', '..', 'config\\settings.ini'))		
		self.settings= configparser.RawConfigParser()
		
		#Create a dict with INI section names as KEYs and INI field names as items in a list that is the VALUE.
		self.section_key_map = {}
		self.section_key_map['info'] = ['last_updated', 'bulk', 'bulk_csv_max']
		self.section_key_map['path'] = ['csv_stor', 'iis_logs', 'logging', 'log_done', 'csv', 'app', 'bulk_csv', 'file_mover', 'temp', 'bulk_logs', 'logsdone_log', 'runtime_log']	
		
		if not os.path.exists(self.config_path):
			self.generate_ini_file()
		else:
			self.update_value('info', 'last_updated', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))			

	def generate_ini_file(self):
		'''
		Create an ini file and set all of the sections and key/value pairs.
		'''
		if self.dir is None or self.config_path is None:
			raise ArgumentError("ConfigMgr:generate_ini_file:ERROR!", "Bad dir/config_path!")
		else:
			print ("Creating settings.ini file...")
			self.settings['info'] = {'last_updated': datetime.datetime.now(),
							    'bulk': 'false',
							    'bulk_csv_max': '100000'}			
			self.settings['path'] = {'iis_logs': os.path.abspath(os.path.join(self.dir, '..', '..', 'iis_log')),
							    'csv': os.path.abspath(os.path.join(self.dir, '..', 'csv')),
							    'bulk_csv': os.path.abspath(os.path.join(self.dir, '..', 'bulk_csv')),
							    'app': os.path.abspath(os.path.join(self.dir, '..', '..', 'app')),
							    'logging': os.path.abspath(os.path.join(self.dir, '..', '..', 'app_logs')),
							    'csv_stor': os.path.abspath(os.path.join(self.dir, '..', '..', '..', 'iisLogCsv')),
							    'log_done': os.path.abspath(os.path.join(self.dir, "Q:\\soft\Leads\\web\\log_done")),
							    'file_mover': os.path.abspath(os.path.join(self.dir, '..', 'file_mover.py')),
							    'temp': os.path.abspath(os.path.join(self.dir, '..', '..', 'temp')),
							    'bulk_logs': os.path.abspath(os.path.join(self.dir, '..', '..', 'temp\\bulk_logs')),
							    'logsdone_log': os.path.abspath(os.path.join(self.dir, '..', '..', 'app_logs\\logs_done.txt')),
							    'runtime_log': os.path.abspath(os.path.join(self.dir, '..', '..', 'app_logs\\run_time.log'))}
			
			with open(self.config_path, 'w') as configfile:
				self.settings.write(configfile)
	
	def update_value(self, section=None, key=None, value=None):
		'''
		Update the VALUE of a KEY found in a specific SECTION in the config file 
		found at file_path.
		'''
		if section is None or key is None or value is None:
			raise ArgumentError("ConfigMgr:update_value:ERROR!", "Bad arg(s)!")
		else:
			self.settings.read(self.config_path)
			self.settings.set(section, key, value)
			with open(self.config_path, 'w') as configfile:
				self.settings.write(configfile)
	
	def get_value(self, config_keys_enum=None):
		'''
		Get the VALUE of a KEY in a SECTION of the INI file.
		Using the dict 'section_key_map' that holds the SECTIONs as the
		keys and their values are the KEYs found in the various SECTIONs.
		'''
		if config_keys_enum is None:
			raise ArgumentError("ConfigMgr:get_value:ERROR!", "Bad config_keys_enum!")
		else:
			key_name = ConfigKeys(config_keys_enum).name
			for k,v in self.section_key_map.items():
				if key_name in v:
					section = k
					self.settings.read(self.config_path)
					return self.settings.get(section, key_name)
	
	def dir_exists(self, dir_path):
		'''
		Check that the directory or file exists.
		'''
		return os.path.exists(dir_path)