import os
from ftplib import FTP

class FtpClient(object):
	def __init__(self):
		#~ HOST = '' #Home.  Check 'ip addr' in a terminal on the server to get IP.
		HOST = '' #Work. Check 'ipconfig' in a terminal on workstation to get 'VirtualBox Host Only' IP.
		USER = 'bcftp'
		PASSWD = ''
		self.ftp = FTP(HOST, USER, PASSWD)
		self.upload_files = []
		
	def upload(self, file):
		if file in self.upload_files: return
		else: self.upload_files.append(file)
		
		# Get to the correct directory
		self.ftp.cwd("ftpstor")
		
		#~ self.ftp.dir()		
		
		put_file = os.path.basename(file)
		cmd = 'STOR {}'.format(put_file)
		with open(file, 'rb') as file_object:
			self.ftp.storbinary(cmd, file_object)		
		
	def close_connection(self, file):
		self.upload_files.remove(file)
		self.ftp.close()
