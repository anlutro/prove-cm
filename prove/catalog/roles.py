class Role:
	"""
	A role is a collection of states, variables and variable files.
	"""
	def __init__(self, name, states, variables, variable_files):
		self.name = name
		assert isinstance(states, list)
		self.states = states
		assert isinstance(variables, dict)
		self.variables = variables
		assert isinstance(variable_files, list)
		self.variable_files = variable_files

	@classmethod
	def from_dict(cls, name, data):
		return cls(
			name,
			states=data.get('states', []),
			variables=data.get('variables', {}),
			variable_files=data.get('variable_files', []),
		)
