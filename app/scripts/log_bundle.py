import sys, json, csv
from enum import Enum
from scripts.exceptions import ArgumentError
from scripts.logger import Logger
from scripts.logger import LoggerType

logger = Logger()

class UriStem(Enum):
	cmupdate = 0
	cmaction = 1
	#~ update1t = 1

class LogBundle(object):	
	def __init__(self, csv_dir=None):		
		if csv_dir is None:			 
			raise ArgumentError("LogBundle:__init__:ERROR!", "No csv_dir passed into ctor.")
		else:
			'''
			The directory on Windows should be like this:
			D:\\workspace\\python\\IIS_LogFile_Viewer\\csv\\
			It must end in a back slash.
			'''
			if csv_dir[1:4] is not "\\":
				csv_dir += "\\"
				logger.log(LoggerType.info, "CSV dir: %s" % csv_dir)
			self.csv_dir = csv_dir
		
		''' Master list of uri stems that we will be looking for.
		If the uri stem exists for a log then that log will get
		parsed.  Otherwise the log is ignored.
		Parallel with the UriStem enum.
		'''
		self.uri_stems = []
		self.uri_stems.append("/cmupdate.asp")	# at index zero, 
		self.uri_stems.append("/cmaction.asp")	# at index one, 
		#Example:
		#~ self.uri_stems.append("/update1t.asp")	# at index ...
		
		# Lists of dicts
		self.cm_logs = [] 
		self.cma_logs = []
		#Example:
		#~ self.u1t_logs = []
		
		# A dictionary to hold the KEY: uriStem VALUE: list of dicts
		self.logs = {}
		self.logs[self.uri_stems[UriStem.cmupdate.value]] = self.cm_logs
		self.logs[self.uri_stems[UriStem.cmaction.value]] = self.cma_logs
		#Example:
		#~ self.logs[self.uri_stems[UriStem.update1t.value]] = self.u1t_logs
	
		'''
		The below lists are the header lines for the CSV files.  Each log type gets its own 
		header and csv file.
		'''
		#CMUpdate.asp log header
		self.cm_header = ['key', 's','date','time','n','uid','clientIp','e','p','c','crwho','crtyp','crid',
		'crstt','crsi','pdclr','v','r','vr','query','userAgent','testall','uriStem','C9']
		
		#CMAction.asp log header
		self.cma_header = ['key','s','date','time','clientIp','cract','crsqt','crwho','crtyp','pdclr','crid',
		'crsi','query','userAgent','uriStem','C9']
		
		#Example: Update1t.asp log header
		#~ self.u1t_header = ['key', 's','date','time','n','uid','clientIp','e','p','c','wn','op','yr','log1tp',
		#~ '1tp','2t','ecfdat','1tm','jf','e1x','e2x','sid','ewz','dfn','dtfe','ecf','ch',
		#~ 'j','b23','bff','defic','vr','v','r','pln13','query','userAgent','testall','edu','cid','uriStem']
		
		# A dictionary to hold the KEY: uriStem VALUE: header list
		self.headers = {}
		self.headers[self.uri_stems[UriStem.cmupdate.value]] = self.cm_header
		self.headers[self.uri_stems[UriStem.cmaction.value]] = self.cma_header
		#Example:
		#~ self.headers[self.uri_stems[UriStem.update1t.value]] = self.u1t_header
		
	def save_dict(self, uri_stem, dict):
		'''
		Depending upon the uriStem of the log, the dict gets saved in a specific list.
		This method also fires off three other methods that make sure the dict has all
		the values it needs to be a good csv row, that the values are reasonable for their 
		type, and that the values don't have commas or spaces in them.
		'''		
		dtmp = self.clean_values(dict)
		
		if uri_stem in self.headers.keys():					
			dict = self.pad_dict(self.headers[uri_stem], dict)		# Make sure all columns have a value.
			dict = self.verify_values(dict)					# Make sure there are no empty cells.
			if self.is_valid_log(dict):
				temp_list = self.logs[uri_stem]				# Get the logs for this uri as a list of dicts.
				temp_list.append(dict)					# Add the new dict to the correct list.			
				self.logs[uri_stem] = temp_list				# Store the newly updated list.
	
	def clean_values(self, dict):
		'''
		Do any further cleaning up of the VALUES that will eventually become
		csv values.  		
		'''
		chars_to_remove = [',', ' ']
		
		for k,v in dict.items():
			val = str(v)
			val = val.translate({ord(i):None for i in chars_to_remove})
			dict[k] = val
		return dict
	
	def pad_dict(self, headers, dict):
		'''		
		The dict must contain all of the fields found in the header list for that type
		of log.  Making it null helps filter out bad logs that can't have a null value
		for certain fields.
		'''		
		for f in headers:
			if f not in dict:
				dict[f] = 'null'
		return dict	
	
	def verify_values(self, dict):
		'''Make sure that each key has a string value. '''
		for k,v in dict.items():
			if dict[k] is None:
				logger.log(LoggerType.info, "dict[%s] is None" % k)
				dict[k] = "null"		
		return dict
		
	def is_valid_log(self, dict):
		'''If the dict passed in has 'null', nothing, or is 'DEMO' for the serial number key, then the 
		log is not valid and we don't want to save it.'''
		retval = True
		sn = ""
		for k,v in dict.items():
			if k is 's' or k is 'r': 					# If the key is SerialNumber or BCRelease
				if k is 's': sn = v					# DEBUG grab serialnumber
				isNull = v is 'null'					# Is the value null?
				isDemo = 'DEMO' in v 				# Does the value contain DEMO?				
				isEmpty = len(v.strip(' \t\n\r')) < 1		# Is the value empty?
				if isNull or isDemo or isEmpty:
					retval = False
			
		return retval					
		
	def flush(self, filename):
		self.flush_toCSV(filename)
			
	def flush_toCSV(self, filename):
		'''
		Write a CSV file for every 'uri stem' found in the list
		self.uri_stems.  There should be a corresponding list
		of dicts that contain the log info found in self.logs.
		'''
		for s in self.uri_stems:
			'''The filename will end up being characters 1 through 3
			of the uri_stem, an underscore, and the log file name.
			They turn out to look like this:
			cmu_ex150119.csv
			upd_ex150119.csv'''
			self.to_CSV(s, s[1:4] + '_' + filename)
		
	def to_CSV(self, uri_stem, filename):
		'''
		Converts the lists defined in __init__ to CSV.
		The csv files are written out to a directory.
		This method expects a filename like the below.
		This is an existing naming convention that Carl uses:
			format	: exYYmmDD.log
			Ex.		: ex150125.log
		'''
		if len(self.logs[uri_stem]) is 0: return
		
		name = filename[:-4] # Get the log filename minus the '.log' ext.
		
		self.write_csv(self.csv_dir + name + '.csv',
				self.headers[uri_stem],
				self.logs[uri_stem])
	
	def write_csv(self, filepath, headers, logs):
		'''
		Create, write, and save a new csv file.
		Params:
			filepath	: The path to save the new csv file to.
			headers	: The header line for the csv file.
			logs		: A list of dicts that hold the log's info.
		'''
		with open(filepath, 'w', newline='') as output_file:
			dict_writer = csv.DictWriter(output_file, headers)
			dict_writer.writeheader()
			dict_writer.writerows(logs)
	
	def to_JSON(self):
		'''
		Converts the lists defined in __init__ to JSON.
		'''
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
		
	def clear(self):
		'''Empty the log dict lists so a new log files logs can be written.'''
		for k in self.logs.keys():
			self.logs[k] = []