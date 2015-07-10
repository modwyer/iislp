import sys, os, psutil, shutil, subprocess, time
from os import path
from scripts.logfilereader import LogFileReader
from scripts.logprocessor import LogProcessor
from scripts.log_bundle import LogBundle
from scripts.file_io_mgr import FileIOMgr
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys
from scripts.logger import Logger
from scripts.logger import LoggerType

logger = Logger()

class AppController(object):
	'''
	Controls the flow of the scripts that read and parse all of the log files.
	'''	
	def __init__(self, settings, args):
		#DEBUG
		#~ logger.log(LoggerType.info, "TEST LoggerType.info...")
		#~ logger.log(LoggerType.error, "TEST LoggerType.error...")
		#~ logger.log(LoggerType.warn, "TEST LoggerType.warn...")
		#~ logger.log(LoggerType.debug, "TEST LoggerType.debug...")
		#~ logger.log(LoggerType.critical, "TEST LoggerType.critical...")
		#DEBUG
		
		# Get the command line args and settings.
		self.settings = settings
		self.args = args	
		
		# Display logging output to console during execution?
		if "verbose" in self.args.keys():
			logger.set_verbosity(self.args["verbose"])
		
		# Set config value for 'bulk' key.  This decides whether
		# to write a big 100k row csv file or one csv file per log type
		# per log file.
		if "bulk" in self.args.keys():
			self.bulk_value = "true"
		else:
			self.bulk_value = "false"
			
		# Get settings info from configuration file.
		logger.log(LoggerType.info, "Getting configuration settings...")	
		self.config_mgr 		= ConfigMgr()		
		self.csv_dir 		= self.config_mgr.get_value(ConfigKeys.csv)
		self.file_mover_path 	= self.config_mgr.get_value(ConfigKeys.file_mover)		
		self.config_mgr.update_value("info", "bulk", self.bulk_value)
		
		print ("App output sent to: ", self.config_mgr.get_value(ConfigKeys.logging) + "\\run_time.log")
		print ("Running...")

		launch_watcher(self.file_mover_path)
		time.sleep(2)												#Give the file watcher a chance to get settled.
		
		self.logreader 		= LogFileReader() 							
		self.log_bundle 		= LogBundle(self.csv_dir)		
		self.log_processor 	= LogProcessor()  							
		self.file_io_mgr 		= FileIOMgr()								
				
		'''Get a list of all the files found in logs_dir.'''
		files = self.file_io_mgr.get_files()
		logger.log(LoggerType.info, "Found %s log files..." % len(files))
		
		'''Process all of the files found in logs_dir in 10 log batches.'''
		for batch in get_batches(files, 10):
			self.process_batch(batch)
				
		# Wait here until the csv_dir is empty of all files.
		logger.log(LoggerType.info, "Done reading log files...")		
		logger.log(LoggerType.info, "Waiting for processing to complete...")
		
		while True:
			csvs = [f for f in os.listdir(self.csv_dir) if os.path.isfile(os.path.join(self.csv_dir,f))]
			if len(csvs) < 1:
				logger.log(LoggerType.info, "CSV directory is empty...")
				break
		
		
		print ("Cleaning up...")
		if self.bulk_value in "true":
			bulk_logs_path = self.config_mgr.get_value(ConfigKeys.bulk_logs)
			shutil.rmtree(bulk_logs_path)
			
		logger.log(LoggerType.info, "Killing all processes...")
		me = os.getpid()
		kill_proc_tree(me)

	def process_batch(self, batch):
		'''Process a batch of logs.'''
		for filepath in batch:
			filename = filepath[-12:]
			logger.log(LoggerType.info, "Filename: %s" % filename)	
			self.logreader.set_path(filepath)   							# Tell the reader what file to read.
			raw_logs = self.logreader.get_logs_raw()               				# Read in the raw logs.
			self.log_processor.set_raw_logs(raw_logs)   					# Give the processor the raw_logs to process.
			self.log_bundle = self.log_processor.process(self.log_bundle)   		# Process the raw logs, returning a bundle of logs.					
			self.log_bundle.flush(filename)								# Save log file log info out to a csv file.						
			self.log_bundle.clear()									# Clear the log bundle so it can be filled again.
	
def get_batches(lst, n):
	""" Yield successive n-sized chunks from lst."""    
	for i in range(0, len(lst), n):
		yield lst[i:i + n]

def launch_watcher(filepath):
	'''Start up the directory watcher process as a subprocess of this one.'''
	#~ p = subprocess.Popen(['python', 'C:\IIS_LogFile_Viewer\IIS_LogFile_Viewer\scripts\csv_dir_watcher.py'])
	#~ p = subprocess.Popen(['python', '..\csv_dir_watcher.py'])
	p = subprocess.Popen(["python", filepath])

def kill_proc_tree(pid, including_parent=True):
	'''http://stackoverflow.com/questions/1230669/subprocess-deleting-child-processes-in-windows'''
	parent = psutil.Process(pid)
	for child in parent.children(recursive=True):
		child.kill()
	if including_parent:
		parent.kill()		
		log_bundle = self.log_proc.process(filename)   						# Process the logs, returning a bundle of logs.