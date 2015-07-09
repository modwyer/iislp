import os, time, psutil
from ftp_client import FtpClient
from exceptions import ArgumentError
from logger import Logger
from scripts.config_mgr import ConfigMgr
from scripts.config_mgr import ConfigKeys
'''http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html'''

logger = Logger()
logger.log_info("DirWatcher is running...")

config_mgr = ConfigMgr()				#New configuration file manager.	

path_to_watch = config_mgr.get_value(ConfigKeys.csv)

before = dict ([(f, None) for f in os.listdir (path_to_watch)])		# Get all files in path_to_watch.

while 1:
	time.sleep (1)
	after = dict ([(f, None) for f in os.listdir (path_to_watch)])  	# Get all files in path_to_watch again.
	added = [f for f in after if not f in before]				 	# What's new and different between before and after?
	removed = [f for f in before if not f in after]			 	# What is no longer there?
	if added: 
		'''
		If there are items in 'added' then stay here until 
		we have looped over all of those items.
		'''
		while True:
			for f in added:
				file = path_to_watch + "\\" + f
				try:
					ftp_client = FtpClient()				# Create new ftp client.
					ftp_client.upload(file)					# Upload the csv file.
					logger.log_info("(ftp'ing...%s)" % file)
					ftp_client.close_connection(file)			# Close the ftp conneciton.
				except ArgumentError as ae:
					logger.log_error(ae.expr, ae.msg)
				finally:
					logger.log_info("(deleting...%s)"  % file)
					time.sleep(2)						# Let the ftp release the file.
					if os.path.isfile(file):
						os.remove(file)					# Delete the file that was just uploaded.
			break
	before = after
	
