import sys
from enum import Enum
from scripts.exceptions import ArgumentError

'''
Log Fields: date time s-ip cs-method cs-uri-stem cs-uri-query s-port cs-username c-ip cs(User-Agent) sc-status sc-substatus sc-win32-status

Date				date			The date that the activity occurred.
Time				time			The time that the activity occurred.
Server IP Address	s-ip			The IP address of the server on which the log entry was generated.
Method			cs-method		The action the client was trying to perform (for example, a GET method).
URI Stem			cs-uri-stem	The resource accessed; for example, Default.htm.
URI Query			cs-uri-query	The query, if any, the client was trying to perform.
Server Port		s-port		The port number the client is connected to.
User Name		cs-username	The name of the authenticated user who accessed your server. This does not include anonymous users, who are represented by a hyphen (-).
Client IP Address	c-ip			The IP address of the client that accessed your server.
User Agent		cs(User-Agent)	The browser used on the client.
Protocol Status		sc-status		The status of the action, in HTTP or FTP terms.
Protocol Substatus  	sc-substatus  	The substatus error code.
Win32 Status		sc-win32-status	The status of the action, in terms used by Microsoft Windows.

Member names: date, time, serverIp, clientAction, stem, query, serverPort, username, clientIp, userAgent, protocolStatus, protocolSubstatus, win32status
'''
class LogFields(Enum):
	date 				= 0
	time 				= 1
	serverIp 			= 2
	clientAction 		= 3
	uriStem 			= 4
	query 			= 5
	serverPort 		= 6
	username 			= 7
	clientIp 			= 8
	userAgent 			= 9
	protocolStatus 		= 10
	protocolSubstatus 	= 11
	win32status 		= 12

class GenericLog(object):
	'Defines a log object created from an IIS log entry.'	
	
	def __init__(self, loginfo=None):
		if loginfo is None:			
			raise ArgumentError("Log:__init__:ERROR!", "No log info passed into ctor.")
		else:
			self.logdata = loginfo
			self.fields = {}	#Init the fields dictionary.
						
			for x in range(0, 12):
				'''
				Loop the loginfo and fill in the fields dict.
				KEY		: LogFields(INT x).name 
				VALUE  	: loginfo item at index 'x'
				'''
				self.fields[LogFields(x).name] = loginfo[x]
	
	def get_field_value(self, fieldIndex):
		if self.fields[LogFields(fieldIndex).name] is None:
			return "null"
		else:
			return self.fields[LogFields(fieldIndex).name]