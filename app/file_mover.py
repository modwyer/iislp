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
		self.bulk 			= self.config_mgr.get_value(ConfigKeys.bulk)		# Create bulk CSV file or not?
		self.csv_store 		= self.config_mgr.get_value(ConfigKeys.csv_stor)	# Get the path to save CSV files.		
		
		self.before = dict ([(f, None) for f in os.listdir (self.path_to_watch)])		# Get all files in path_to_watch.

	def run(self):
		'''http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html'''
		while 1:
			time.sleep (1)
			after = dict ([(f, None) for f in os.listdir (self.path_to_watch)])  		# Get all files in path_to_watch again.
			added = [f for f in after if not f in self.before]				 		# What's new and different between before and after?
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
							logger.log_error(ae.expr, ae.msg)
						#~ finally:
							#~ time.sleep(4)							
							#~ if os.path.isfile(file):
								#~ os.remove(file)						# Delete the file that was just moved.
					break
			before = after
	
	def move_file(self, file=None):	
		logger.log(LoggerType.info,  "Moving file: %s" % file)
		if file is None:
			return
		bulk = self.bulk.lower()
		print ("bulk: ", bulk)
		if bulk in 'false':
			self.move_csv(file)
		if bulk in 'true':
			self.move_bulk(file)			

	def move_csv(self, src):
		shutil.copy2(src, self.csv_store)
		
	def move_bulk(self, file):	
		log_type = file[-16:-13] #Ex. 'cmu', 'cma'
		csv_file = "\\" + log_type + "_bulk.csv"
		dest_dir = self.config_mgr.get_value(ConfigKeys.bulk_csv) + csv_file;
				
		self.csv_writer = CsvWriter(dest_dir)
		self.csv_writer.append_file(file)
		
		#~ count = self.csv_writer.get_row_count()
		
		# Open the newly made csv file, read in its rows, decide
		# whether to keep the header or not and append the rows
		# to another 'bulk' csv file.
		# If the bulk csv file is close to over over 100k rows, then
		# save it as a copy with a timestamp in the name to make it unique.
		# Then make a new bulk csv file and do fill it and so on.
		
		#~ f = open(file, 'r')
		#~ reader = csv.reader(f)
				
		#~ if count is 0:
			#~ header = next(reader)	#Remove the header line.
			#~ self.csv_writer.add_record(header)  #Save the header line.
		#~ else:
			#~ next(reader, None)	#Remove the header
		
		# Add rows to csv writer.
		#~ for row in reader:
			#~ self.csv_writer.add_record(row)
		
		#~ f.close()		
		#~ self.csv_writer.flush()	# Write out new csv content.
		
		# Remove the CSV file from the CSV directory.
		remove_file(file)	

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