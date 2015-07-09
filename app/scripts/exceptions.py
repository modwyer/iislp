import sys

class ArgumentError(Exception):
	'''
	Exception raised for errors with arguments.
	Attributes:
		expr -- who is throwing a problem with their argument(s)
		msg -- explanation of the error
	'''
	def __init__(self, expr, msg):
		self.expr = expr
		self.msg = msg
	def __str__(self):
		return repr(self.msg)