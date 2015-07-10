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
		self.filename = outputpath 							# CSV file to write to.
		self.row_count = self.get_row_count()				# Total rows in the outputpath CSV file.
		
		# If the CSV file already has 100k+ rows then save a copy of it with
		# a timestamp in the name, then remove the large CSV file  so a new 
		# CSV file will be created in the next 'flush'.
		if self.row_count > 15000:		
			logger.log(LoggerType.info, "Bulk CSV file reached 100k rows...")
			
			# Make the filename of the copy.
			copy_name = self.filename[:-4]					# All but '.csv'.
			t = time.localtime()
			timestamp = time.strftime('%y%m%d_%H%M%S', t)		# Timestamp: Ex. 150707_202456
			dest = copy_name + "_" + timestamp + ".csv"		# All together as full filename.
			
			logger.log(LoggerType.info, "Saving a version named: %s" % dest)
			
			shutil.copy2(self.filename, dest)					# Save a copy of the file with the new name.
			
			if os.path.exists(dest):						# If the version just saved exists...
				logger.log(LoggerType.info, "Deleting: %s" % self.filename)
				os.remove(self.filename)					# Remove the current bulk csv file.
			else:
				raise ArgumentError("CsvWriter:__init__:ERROR!", "dest %s does not exist!" % dest)
		
	def append_file(self, file):
		count = self.get_row_count()
		
		f = open(file, 'r')
		reader = csv.reader(f)
				
		if count is 0:
			header = next(reader)						#Read and save the header line.
			self.add_record(header)  						#Add the header line as a row.
		else:
			next(reader, None)							#Remove the header line.
		
		for row in reader:
			self.add_record(row)							# Add rows to csv writer.
		
		f.close()		
		self.flush()									# Write out new csv content.
		
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
		else:
			logger.log(LoggerType.info, "No data exists.  Nothing written.")