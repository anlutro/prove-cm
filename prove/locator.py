import collections
import glob
import logging
import os
import os.path

from prove.environment import Role, VariableFile
from prove.states import StateFile
import prove.util

LOG = logging.getLogger(__name__)


class LocatorException(Exception):
	pass

class LoaderNotFoundException(LocatorException):
	def __init__(self, path):
		super().__init__('No loader found for file: ' + path)


def _get_file_name(path, root_dir, strip_extension=True, component=None):
	name = path.replace(root_dir, '')
	name = name.lstrip(os.sep)
	if strip_extension:
		name = name.split('.')[0]
	if component:
		name = component + '/' + name
	return name


class Component:
	def __init__(self, name, roles, state_files, variable_files, files):
		self.name = name
		self.roles = roles
		self.variable_files = variable_files
		self.state_files = state_files
		self.files = files


class Locator:
	def __init__(self, root_dir, loaders):
		self.root_dir = root_dir
		self.loaders = loaders

	def locate_roles(self, component=None):
		if component:
			roles_file = self._get_component_file(component, 'roles')
			if roles_file:
				LOG.debug('Found role file: %s -- %s', component, roles_file)
				return {component: self._load_file_data(roles_file)}
		roles_dir = self._get_path('roles', component)
		paths = prove.util.list_files(roles_dir)
		roles = collections.OrderedDict()
		for path in paths:
			name = _get_file_name(path, roles_dir, component=component)
			data = self._load_file_data(path)
			roles[name] = Role.from_dict(name, data)
			LOG.debug('Found role: %s', name)
		return roles

	def locate_states(self, component=None):
		if component:
			state_file = self._get_component_file(component, 'states')
			if state_file:
				LOG.debug('Found state: %s -- %s', component, state_file)
				loader_module = self._get_loader(state_file)
				state_file = StateFile(component, state_file, loader_module)
				return {component: state_file}
		states_dir = self._get_path('states', component)
		paths = prove.util.list_files(states_dir)
		state_files = collections.OrderedDict()
		for path in paths:
			name = _get_file_name(path, states_dir, component=component)
			loader_module = self._get_loader(path)
			state_file = StateFile(name, path, loader_module)
			state_files[name] = state_file
			LOG.debug('Found state: %s -- %s', name, path)
		return state_files

	def locate_variables(self, component=None):
		if component:
			variables_file = self._get_component_file(component, 'variables')
			if variables_file:
				data = self._load_file_data(variables_file)
				LOG.debug('Found variable file: %s -- %s', component, variables_file)
				return {component: VariableFile(component, data)}
		variables_dir = self._get_path('variables', component)
		paths = prove.util.list_files(variables_dir)
		variable_files = collections.OrderedDict()
		for path in paths:
			name = _get_file_name(path, variables_dir, component=component)
			data = self._load_file_data(path)
			variable_files[name] = VariableFile(name, data)
			LOG.debug('Found variable file: %s -- %s', name, path)
		return variable_files

	def locate_files(self, component=None):
		files_dir = self._get_path('files', component)
		files = {}
		for path in prove.util.list_files(files_dir):
			name = _get_file_name(path, files_dir, strip_extension=False, component=component)
			files[name] = path
			LOG.debug('Found file: %s -- %s', name, path)
		return files

	def locate_components(self):
		components_dir = self._get_path('components')
		components = []
		for component_name in prove.util.list_subdirs(components_dir):
			LOG.debug('Found component: %s', component_name)
			roles = self.locate_roles(component_name)
			state_files = self.locate_states(component_name)
			variable_files = self.locate_variables(component_name)
			files = self.locate_files(component_name)
			components.append(Component(
				component_name, roles, state_files, variable_files, files
			))
		return {component.name: component for component in components}

	def _get_path(self, name, component=None):
		root_dir = self.root_dir
		if component:
			root_dir = os.path.join(root_dir, 'components', component)
		return os.path.join(root_dir, name)

	def _get_component_file(self, component, file_name):
		component_dir = os.path.join(self.root_dir, 'components', component)
		LOG.debug('Globbing %s', os.path.join(component_dir, file_name + '.*'))
		paths = glob.glob(os.path.join(component_dir, file_name + '.*'))
		for loader in self.loaders:
			for path in paths:
				if loader.supports(path):
					return path
		return None

	def _get_loader(self, path):
		for loader in self.loaders:
			if loader.supports(path):
				return loader
		raise LoaderNotFoundException(path)

	def _load_file_data(self, path):
		return self._get_loader(path).load(path)
