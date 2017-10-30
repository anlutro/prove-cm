class VariableFile:
	"""
	A file on the master filesystem containing variables.
	"""
	def __init__(self, name, variables):
		self.name = name
		self.variables = variables
