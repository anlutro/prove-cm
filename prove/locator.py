import collections
import os
import os.path

from prove.environment import Role, VariableFile
from prove.state import StateFile
import prove.util


class LocatorException(Exception):
	pass

class LoaderNotFoundException(LocatorException):
	def __init__(self, path):
		super().__init__('No loader found for file: ' + path)


def _get_file_name(path, root_dir):
	name = path.replace(root_dir, '')
	name = name.lstrip(os.sep)
	name = name.split('.')[0]
	return name


class Locator:
	def __init__(self, root_dir, loaders):
		self.root_dir = root_dir
		self.loaders = loaders

	def locate_roles(self):
		roles_dir = os.path.join(self.root_dir, 'roles')
		paths = prove.util.list_files(roles_dir)
		roles = collections.OrderedDict()
		for path in paths:
			name = _get_file_name(path, roles_dir)
			data = self._load_file_data(path)
			roles[name] = Role.from_dict(name, data)
		return roles

	def locate_states(self):
		states_dir = os.path.join(self.root_dir, 'states')
		paths = prove.util.list_files(states_dir)
		state_files = collections.OrderedDict()
		for path in paths:
			name = _get_file_name(path, states_dir)
			loader_module = self._get_loader(path)
			state_file = StateFile(name, path, loader_module)
			state_files[name] = state_file
		return state_files

	def locate_variables(self):
		variables_dir = os.path.join(self.root_dir, 'variables')
		paths = prove.util.list_files(variables_dir)
		variable_files = collections.OrderedDict()
		for path in paths:
			name = _get_file_name(path, variables_dir)
			data = self._load_file_data(path)
			variable_files[name] = VariableFile(name, data)
		return variable_files

	def _get_loader(self, path):
		for loader in self.loaders:
			if loader.supports(path):
				return loader
		raise LoaderNotFoundException(path)

	def _load_file_data(self, path):
		return self._get_loader(path).load(path)
