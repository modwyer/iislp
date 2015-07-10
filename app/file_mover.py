import sys, os, time, psutil, shutil, errno, csv
from scripts.exceptions import ArgumentError
from scripts.logger import Logger
from scripts.logger import LoggerType
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys
from scripts.csvwriter import CsvWriter

logger = Logger()

class FileMover(object):
	def __init__(self):
		logger.log(LoggerType.info, "FileMover is running...")
		
		self.config_mgr = ConfigMgr()											
		self.path_to_watch 	= self.config_mgr.get_value(ConfigKeys.csv)		# Get the path to where the app-generated CSV files end up.		
		self.csv_store 		= self.config_mgr.get_value(ConfigKeys.csv_stor)	# Get the path to save CSV files.			
		
		self.before = dict ([(f, None) for f in os.listdir (self.path_to_watch)])		# Get all files in path_to_watch.

	def run(self):
		'''http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html'''
		while 1:
			time.sleep (1)
			after = dict ([(f, None) for f in os.listdir (self.path_to_watch)])  		# Get all files in path_to_watch again.
			added = [f for f in after if not f in self.before]				 	# What's new and different between before and after?
			removed = [f for f in self.before if not f in after]				# What is no longer there?
			
			if added: 
				'''
				If there are items in 'added' then stay here until 
				we have looped over all of those items.
				'''
				while True:
					for f in added:
						file = self.path_to_watch + "\\" + f
						try:
							self.move_file(file)
						except ArgumentError as ae:
							logger.log(LoggerType.error, ae.expr, ae.msg)
					break
			before = after
	
	def move_file(self, file=None):	
		logger.log(LoggerType.info,  "Moving file: %s" % file)

		if file is None:
			logger.log(LoggerType.critical,  "FileMover::move_file::File is None.")
			return
			
		self.bulk = self.config_mgr.get_value(ConfigKeys.bulk)		# Create bulk CSV file or not?
		bulk = self.bulk.lower()			
		print ("self.bulk: ", self.bulk)
		
		if bulk in 'false':
			move_csv(file, self.csv_store)
		if bulk in 'true':
			move_bulk(file, self.config_mgr.get_value(ConfigKeys.bulk_csv) )			

def move_csv(src, csv_stor):		
	fname = src[-16:]											# Get the name of the src file.
	shutil.copy2(src, csv_stor)										# Copy the src file to the destination directory.
	
	remove_file(src)										# Remove the CSV file from the CSV directory.
	
def move_bulk(file, bulk_csv_dir):	
	log_type = file[-16:-13] 										#Ex. 'cmu', 'cma'
	csv_file = "\\" + log_type + "_bulk.csv"
	dest_dir = bulk_csv_dir + csv_file;								# Create dest dir path.
			
	csv_writer = CsvWriter(dest_dir)
	csv_writer.append_file(file)									# Add 'file' rows to bulk csv file for 'log_type'.
			
	remove_file(file)											# Remove the CSV file from the CSV directory.

def remove_file(file):
	if os.path.isfile(file):
		os.remove(file)
	
def main(argv=None):
	fm = FileMover()
	fm.run()
	return 0        # success

if __name__ == '__main__':
	status = main(sys.argv[1:])
	sys.exit(status)