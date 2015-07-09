import sys, uuid
from urllib.parse import parse_qsl
from scripts.logs import LogFields
from scripts.exceptions import ArgumentError

class LogParser(object):
	def __init__(self):
		self.logCounter = {}
		
	def get_basic_info(self, log, ret_dict):
		'''
		Get the basic set of field values from the log 
		that are important to us.
		These are values for fields that every MS IIS Log has.
		
		"LogBasic", ['date', 'time', 'uriStem', 'query', 'clientIP', 'userAgent']		
		'''		
		ret_dict["date"] 	= log.get_field_value(LogFields.date)
		ret_dict["time"] 	= log.get_field_value(LogFields.time)
		ret_dict["uriStem"] 	= log.get_field_value(LogFields.uriStem).lower()
		ret_dict["query"] 	= log.get_field_value(LogFields.query)
		ret_dict["clientIp"] 	= log.get_field_value(LogFields.clientIp)
		ret_dict["userAgent"] 	= log.get_field_value(LogFields.userAgent)		
		return ret_dict
		
	def parse_iis_log(self, uuid, log):
		self.logQs 		= log.get_field_value(LogFields.query)	#Get the log's QueryString.
		query_dict 	= dict(parse_qsl(self.logQs))  			#Parse the query string to a list of tuples and cast to a dict.
		log_dict 		= self.get_basic_info(log, query_dict)  	#Add the log basic info to dict
		log_dict["key"] 	= uuid							#Add the UUID as the key for the log.
		return log_dict