import sys
import getopt
from scripts.app_controller import AppController
from scripts.logger import Logger
from scripts.logger import LoggerType

logger = Logger()

def process_command_line(argv):
	'''Get the command line arguments and store them. '''
	logger.log(LoggerType.info, "****************************")
	logger.log(LoggerType.info, 'Best Case IIS Log Processor')
	logger.log(LoggerType.info, "****************************")
	
	settings = []
	arguments = {}
	
	try:
		opts, args = getopt.getopt(argv, "h:v", ["help","verbose="])
		#~ opts, args = getopt.getopt(argv, "hd:",["help","directory="])
		#~ opts, args = getopt.getopt(argv, "h:",["help"])
	except getopt.GetoptError:
		#~ print ('Usage: iislp.py -d <directory> ')
		logger.log(LoggerType.info, 'Usage: iislp.py')
		sys.exit(2)
	
	'''Retreive values from the args.'''
	for opt, arg in opts:
		if opt == '-h': #Output help info.
			print ('This script parses new logs found in the log_done '
				'directory on the Q: drive.  The log info ends '
				'up stored in a database.\n\n')
			print ('Usage: iislp.py')
			sys.exit()
		elif opt in ("-v", "--verbose"):
			arguments["verbose"] = True;
		#~ elif opt in ("-d", "--directory"):
			#~ arguments["directory"] = arg
	
	return settings, arguments
	
def run(settings, args):
	ac = AppController(settings, args)

def main(argv=None):
	settings, args = process_command_line(argv)
	run(settings, args)
	return 0        # success

if __name__ == '__main__':
	status = main(sys.argv[1:])
	sys.exit(status)