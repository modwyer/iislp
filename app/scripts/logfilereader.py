import sys, uuid
from scripts.logs import GenericLog
from scripts.exceptions import ArgumentError
from scripts.logger import Logger
from scripts.logger import LoggerType

logger = Logger()

class LogFileReader(object):
	'''
	Reads in the lines of an IIS log file that are in the format:
	2014-10-30 09:35:26 192.168.100.65 GET /CMUpdate.ASP crsi=A16347&crid=PetersonMelitzaL1&crstt=1&crwho=cin&crtyp=I3&pdclr=0&uid=STROUSE22&v=23&r=140716&s=37431&vr=P&p=4143900820&n=StrouseLawOffices&c=2865&e=05/23/2015 80 - 174.103.167.105 BestCaseUpdate+CR+Manager 200 0 0
	
	The log fields are space separated and the query string field can be split on 
	the separate variables within.
	'''
	
	logs_raw = [] 		#A List of StringLists.
	log_objects = {}	#Dict of all Log objects.
			
	def set_path(self, filepath=None):
		if filepath is None:			
			raise ArgumentError("TextFileReader:__init__:ERROR!", 
							"No filepath passed into ctor.")
		else:
			logger.log(LoggerType.info, "Filepath: %s " % filepath)
			
			self.filepath = filepath
			# We reuse this class object, so we need to clear the logsRaw and logObjects
			logs_raw = []
			log_objects = {}
	
	def open(self):
		'''Open file for read-only.'''
		self.file = open(self.filepath, 'r')	
	
	def get_logs_raw(self):
		'''
		Read in the 'self.filepath' line by line and store all the logs.
		Returns: a Dict of all Log objects, where a random UUID is the key
		and the value is a StringList of the GenericLog objects.
		'''		
		logger.log(LoggerType.info, "Reading log file...")
		
		self.open()
	
		for line in self.file:
			if line[:1] is not '#':		#Ignore comment lines.
				logvalues = line.split(" ")
				self.logs_raw.append(logvalues)
				try:
					newLog = GenericLog(logvalues) #Create the new Log object.
					#Store the Log object, using a newly generated UUID as the key.
					self.log_objects[uuid.uuid4()] = newLog	
				except ArgumentError as ae:
					err = "Expr: " + ae.expr + "_Msg: " + ae.msg
					logger.log(LoggerType.error, err)		
		
		self.file.close()
		
		return self.log_objects