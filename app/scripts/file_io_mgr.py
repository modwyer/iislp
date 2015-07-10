import sys, os.path, time, datetime, csv, shutil
from scripts.logger import Logger
from scripts.logger import LoggerType
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys

# Create date formats.
date_as_var_format 	= '%Y_%m_%d_%H_%M_%S_%f'
date_format 		= '%Y-%m-%d %H:%M:%S.%f'

# Get some configuration settings.
config_mgr = ConfigMgr()
logs_done_log_path 	= config_mgr.get_value(ConfigKeys.logging) + "\\logs_done.txt"
bulk_logs_dir		= config_mgr.get_value(ConfigKeys.temp) + "\\bulk_logs"
iis_log_dir 		= config_mgr.get_value(ConfigKeys.iis_logs)

logger = Logger()

class FileIOMgr(object):
	
	def get_files(self):
		'''
		This method fires off a few things.
		First we get all the logged log files that have already 
		been processed.  That info is rows of text in a txt file.
		Then we get the list of log files along with their modifed 
		datetime info.  We compare those two	lists to see what 
		new logs are available.  Only the new logs get returned.  
		We also copy the log files to the 'iis_log_dir'	so the app 
		can get at them.		
		'''
		# Get the 'log_file_dir', where the app should look for new logs to process.
		log_file_dir = get_log_file_dir()
		
		# Get the stored list of logs that have been done already.
		logs_done_list = get_logs_done()
		logger.log(LoggerType.info, "Logs 'done' list count: %s" % len(logs_done_list))
		
		# Get last modified datetimes from all files in log_done.
		files_list = get_file_dates_sortAsc(log_file_dir)	
			
		# Get only the logs that are in the log_done folder but not the done list.
		new_logs_files = [f for f in files_list if not f in logs_done_list]
				
		# There should be some checks and balances to be sure that
		# the file was processed and uploaded and all that, successfully.  
		# So, for now, I am just going to write the new logs files names to the logs_done file.
		write_log_done(new_logs_files)
		
		# Items in new_logs_files looks like this:
		#	2012_03_07_16_07_56_052000_ex120214.log
		# Need to get the filename off the end and concat it with the iis log dir.	
		# Take the last 12 characters off each full file name (like the example above)
		# and save them into a list.
		file_names = list(map(lambda x: x[-12:], new_logs_files))
		
		logger.log(LoggerType.info, "Filenames: %s" % file_names)
		
		# Copy the file_names from log_file_dir to iis_log_dir
		for fn in file_names:
			shutil.copy2(log_file_dir + "\\" + fn, iis_log_dir + "\\" + fn)
		
		return list(map(lambda x: log_file_dir + "\\" + x[-12:], new_logs_files))	

def get_log_file_dir():
	'''
	If we are processing in bulk then 100k or so rows go into a csv file.
	Otherwise we process one log file and generate a CSV file per log type.
	For bulk processing we process all the logs found in 'bulk_logs_dir'.
	Otherwise we look in the 'logs_done' dir where the IIS logs are stored.
	'''
	is_bulk = config_mgr.get_value(ConfigKeys.bulk)
	
	if is_bulk in "true":
		log_file_dir = bulk_logs_dir
	else:
		log_file_dir 	= "D:\\workspace\\python\\IIS_LOG_FILE_VIEWER\\iis_log_files_big" 	#TESTING
		#~ log_file_dir 		= config_mgr.get_value(ConfigKeys.log_done)  					#LIVE	
	
	logger.log(LoggerType.info, "IIS Log file dir: %s" % log_file_dir)
	return log_file_dir

def get_file_dates_sortAsc(path):
	file_dates = []
	path_full = path + "\\"
	
	for filename in os.listdir(path):
		if os.path.isfile(os.path.join(path_full, filename)):
			if filename[-4:] in '.log': # .log files only!
				'''Get the last modified date of the file as a datetime.'''
				full_path = os.path.join(path_full, filename)
				date = modification_date(full_path)
				'''
				Concat the filename on the datetime string.
				Use that as the KEY with the VALUE being the filename
				datetime object.
				Format of the datetime components and filename is 
				underscore separated.
				Eg.	year,month,day,hour,min,sec,filename
					2015_03_09_05_18_17_ex150306.log
				'''
				file_str = date.strftime(date_as_var_format)
				file_str += "_" + filename
				file_dates.append(file_str)
	
	return file_dates
			
def modification_date(filename):
	'''Get the date modified for filename.'''
	t = os.path.getmtime(filename)
	return datetime.datetime.fromtimestamp(t)
	
def get_logs_done():
	'''
	Read in the 'logs_done.txt' file that keeps a list of all of the
	log files that have been parsed and added to the database.
	'''	
	logs_done_list = []
	
	with open(logs_done_log_path, 'r') as f:
		for line in f:
			logs_done_list.append(line[0:-1]) # Trim the \n off the end.
	return logs_done_list
	
def write_log_done(list):
	'''
	Log the log files that have been processed.
	'''
	list.sort()
	f = open(logs_done_log_path, 'a')
	'''If list is a list.'''
	for item in list:
		f.write(item + '\n')