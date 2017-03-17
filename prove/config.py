import fnmatch
import re

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


class Group:
	def __init__(
		self,
		name,
		glob=None,
		regex=None,
		roles=None,
		states=None,
		variables=None,
		variable_files=None,
	):
		self.name = name
		assert (glob or regex) and not (glob and regex), (
			'must provide one *and only one* of glob and regex')
		self.glob = glob
		self.regex = regex
		self.roles = roles or []
		self.states = states or []
		self.variables = variables or {}
		self.variable_files = variable_files or []

	def matches(self, target):
		if self.glob:
			return fnmatch.fnmatch(target.name, self.glob)
		if self.regex:
			return bool(re.match(self.regex, target.name))
		return False

	def merge_into(self, target):
		target.roles += self.roles
		target.states += self.states
		target.variables.update(self.variables)
		target.variable_files += self.variable_files


class Target:
	def __init__(
		self,
		host,
		name=None,
		groups=None,
		roles=None,
		states=None,
		variables=None,
		variable_files=None,
		**kwargs
	):
		self.host = host
		self.name = name or host
		self.groups = groups or []
		self.roles = roles or []
		self.states = states or []
		self.variables = variables or {}
		self.variable_files = variable_files or []
		self.options = kwargs

	def __repr__(self):
		return '<%s.%s "%s" at 0x%x>' % (
			self.__module__, self.__class__.__name__, self.name, id(self)
		)
