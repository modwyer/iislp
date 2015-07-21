import logging
from enum import Enum
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys

config_mgr = ConfigMgr()
logging_filepath = config_mgr.get_value(ConfigKeys.logging) + "\\run_time.log"

# Create logger.
logger = logging.getLogger('iislp_logger')
logger.setLevel(logging.DEBUG)

# Create file handler to file where logs will be stored.
fh = logging.FileHandler(logging_filepath)
fh.setLevel(logging.DEBUG)

# Create formatter and add it to the handlers.
formatter = logging .Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

# Add the handlers to the logger.
logger.addHandler(fh)

class LoggerType(Enum):
	info = 0
	error = 1
	warn = 2
	debug = 3
	critical = 4
	
class Logger(object):
	def __init__(self):
		self.verbose = False
			
		self.log_funcs = {}
		self.log_funcs[LoggerType.info] = self.log_info
		self.log_funcs[LoggerType.error] = self.log_error
		self.log_funcs[LoggerType.warn] = self.log_warn
		self.log_funcs[LoggerType.debug] = self.log_debug
		self.log_funcs[LoggerType.critical] = self.log_critical		
		
	def set_verbosity(self, verbose):
		self.verbose = True if verbose else False
	
	def log(self, log_type, msg):
		self.log_funcs[log_type](msg)	# Execute a stored function.
		
	def log_info(self, msg):
		if self.verbose: 
			print (msg)
		logger.info(msg)
	
	def log_error(self, msg):
		if self.verbose: 
			print (msg)
		logger.error(msg)
		
	def log_warn(self, msg):
		if self.verbose: 
			print (msg)
		logger.warn(msg)
		
	def log_debug(self, msg):
		if self.verbose: 
			print (msg)
		logger.debug(msg)
		
	def log_critical(self, msg):
		if self.verbose: 
			print (msg)
		logger.critical(msg)