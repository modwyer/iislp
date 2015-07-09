import sys
from scripts.logs import LogFields
from scripts.logparser import LogParser
from scripts.log_bundle import LogBundle
from scripts.exceptions import ArgumentError
from scripts.logger import Logger
from scripts.logger import LoggerType

logger = Logger()

class LogProcessor(object):
	def __init__(self):		
		self.log_uri_stems = ["/cmupdate.asp", "/cmaction.asp"]
		#~ self.log_uri_stems = ["/cmupdate.asp"]
		self.log_counter = {}				
		self.parser = LogParser()
	
	def set_raw_logs(self, raw_logs=None):
		if raw_logs is None:
			raise ArgumentError("LogProcessor:set_raw_logs:ERROR!", "No raw_logs passed in.")
		
		self.raw_logs = raw_logs	
		# Reset log_counter since we resuse this object
		self.log_counter = {}
		
	def log_counter_uptick(self, key):
		#Increment the logCounter for 'key'.
		'''The variable 'count' is the VALUE in 'self.log_counter[key]'
		if 'key' is a key in self.log_counter.  If 'key' is not found
		then return 0.'''
		count = self.log_counter[key] if key in self.log_counter else 0
		self.log_counter[key] = count + 1			
		
	def process(self, log_bundle):
		'''
		Either process and parse or ignore the passed-in log based on
		its uriStem (Ex. /CMUpdate.ASP, /Update1t.ASP, ...) and whether
		it is found in the log_uri_stems list.
		Returns a LogBundle object.
		'''
		for key, log in self.raw_logs.items():
			uri_stem = log.get_field_value(LogFields.uriStem)
			if uri_stem is not None:
				uri_stem = uri_stem.lower()
				if uri_stem in self.log_uri_stems:
					log_dict = self.parser.parse_iis_log(key, log)
					log_bundle.save_dict(uri_stem, log_dict)
					self.log_counter_uptick(uri_stem)
		
		#Write count info out to console.
		if "/cmupdate.asp" in self.log_counter.keys():
			logger.log(LoggerType.info, "CMUpdate # logs: %s" % self.log_counter["/cmupdate.asp"])
		if "/cmaction.asp" in self.log_counter.keys():
			logger.log(LoggerType.info, "CMAction # logs: %s" % self.log_counter["/cmaction.asp"])
		return log_bundle