import csv, os, shutil, time
from datetime import datetime
from scripts.writetexttofile import Writer
from scripts.exceptions import ArgumentError
from scripts.logger import Logger
from scripts.logger import LoggerType

logger = Logger()

class CsvWriter(object):
	def __init__(self, outputpath=None):
		if outputpath is None:
			raise ArgumentError("CsvWriter:__init__:ERROR!", "Outputpath param is None.")
		self.data = []
		self.datetime = datetime.now().strftime("%Y_%m_%d@%I%M%p")	#Format datetime as 2014_11_10@0232pm
		self.filename = outputpath 	# CSV file to write to.
		self.row_count = self.get_row_count()	# Total rows in the outputpath CSV file.
		print ("row_count: ", self.row_count)
		
		# If the CSV file already has 100k+ rows then rename it with
		# a timestamp so a new CSV file will be created in the next 'flush'.
		if self.row_count > 15000:		
			logger.log(LoggerType.info, "Bulk CSV file reached 100k rows...")
			# Make the filename of the copy.
			copy_name = self.filename[:-4]	# All but '.csv'.
			t = time.localtime()
			timestamp = time.strftime('%y%m%d_%H%M%S', t)	# Timestamp: Ex. 150707_202456
			dest = copy_name + "_" + timestamp +".csv"	# All together as full filename.
			
			logger.log(LoggerType.info, "Saving a version named: %s" % dest)
			
			shutil.copy2(self.filename, dest)	# Save a copy of the file with the new name.
			
			if os.path.exists(dest):		# If the version just saved exists...
				print ("dest exists- deleting ", self.filename)
				os.remove(self.filename)	# Remove the current bulk csv file.
			else:
				raise ArgumentError("CsvWriter:__init__:ERROR!", "dest %s does not exist!" % dest)
		
	def append_file(self, file):
		count = self.get_row_count()
		# Open the newly made csv file, read in its rows, decide
		# whether to keep the header or not and append the rows
		# to another 'bulk' csv file.
		# If the bulk csv file is close to over over 100k rows, then
		# save it as a copy with a timestamp in the name to make it unique.
		# Then make a new bulk csv file and do fill it and so on.
		f = open(file, 'r')
		reader = csv.reader(f)
				
		if count is 0:
			header = next(reader)	#Remove the header line.
			self.add_record(header)  #Save the header line.
		else:
			next(reader, None)	#Remove the header
		
		# Add rows to csv writer.
		for row in reader:
			self.add_record(row)
		
		f.close()		
		self.flush()	# Write out new csv content.
		
	def get_row_count(self): 
		retval = 0
		if os.path.exists(self.filename):
			f = open(self.filename)
			retval = sum(1 for row in f)
		return retval
		
	def add_record(self, record=None):
		if record is None:
			raise ArgumentError("CsvWriter:addRecord:ERROR!", "Record param is None.")
		else:
			self.data.insert(len(self.data), record)
			
	def flush(self):
		if len(self.data) > 0:
			logger.log(LoggerType.info, "Writing %d records (includes HEADER) to CSV file..." % len(self.data))
			with open(self.filename, 'a+', newline='') as csvfile:
				writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				for row in self.data:
					writer.writerow(row)
					
				logger.log(LoggerType.info, "CSV write success...")
				logger.log(LoggerType.info, "Output saved to: \"%s\"" % self.filename)
				logger.log(LoggerType.info, "Finished at: %s" % self.datetime)
