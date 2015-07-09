import sys

class Writer(object):
	"""Class to write text to files."""
	
	def append(self, outfilepath, outtext):
		with open(outfilepath, "a") as text_file:
			text_file.write(outtext)
			
	def appendList(self, outfilepath, list):
		with open(outfilepath, "a") as text_file:
			for entry in list:
				#Each entry in the List is appended as its own line.
				text_file.write(', '.join(entry) + "\n")