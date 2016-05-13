import prove.util


class Options:
	def __init__(self, data):
		assert isinstance(data, dict)
		self.data = data

	def get(self, key, default=None):
		return self.data.get(key, default)

	def __getitem__(self, key):
		return self.data[key]

	def make_copy(self, overrides):
		return Options(prove.util.deep_dict_merge(self.data, overrides))

	def __repr__(self):
		return repr(self.data)


class HostConfig:
	def __init__(self,
		host,
		name=None,
		roles=None,
		states=None,
		variables=None,
		variable_files=None,
		**kwargs
	):
		self.host = host
		self.name = name or host
		self.roles = roles or []
		self.states = states or []
		self.variables = variables or {}
		self.variable_files = variable_files or []
		self.options = kwargs
