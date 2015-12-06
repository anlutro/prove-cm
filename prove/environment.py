import collections
import importlib
import os.path
import prove.utils


class Role:
	def __init__(self, name, path):
		self.name = name
		self.path = path


class Variable:
	def __init__(self, name, path):
		self.name = name
		self.path = path


class State:
	def __init__(self, name, path):
		self.name = name
		self.path = path


class Component:
	def __init__(self, name, roles, variables, states):
		self.name = name
		self.roles = roles
		self.variables = variables
		self.states = states


class FileLoader:
	def __init__(self, root_path, loaders):
		self.root_path = root_path
		self.loaders = [importlib.import_module('prove.loader.' + loader) for loader in loaders]

	def load_role(self, role):
		return self._load(role.path, {})

	def load_variable(self, variable, variables):
		return self._load(variable.path, variables)

	def load_state(self, state, variables):
		return self._load(state.path, variables)

	def _load(self, path, variables):
		for loader in self.loaders:
			if loader.supports(path):
				return loader.load(path, variables)
		raise Exception('Cannot find loader for file: ' + path)


def _scan(root_path, directory, cls):
	'''Scan a directory for files and instantiate them as either Role, Variable
	or State objects.'''
	root_path = os.path.join(root_path, directory)
	files = prove.utils.list_files(root_path)
	ret = {}
	for path in files:
		name = path.replace(root_path, '').lstrip('/').split('.')[0]
		ret[name] = cls(name, path)
	return ret


def _scan_components(components_dir):
	components = []
	if os.path.isdir(components_dir):
		component_dirs = [d for d in os.listdir(components_dir)
			if os.path.isdir(os.path.join(components_dir, d))]
		for component_dir in component_dirs:
			component_name = component_dir
			component_dir = os.path.join(components_dir, component_name)
			components.append(Component(
				component_dir,
				_scan(component_dir, 'roles', Role),
				_scan(component_dir, 'variables', Variable),
				_scan(component_dir, 'states', State),
			))
	return components


class Environment:
	def __init__(self, loader, roles, variables, states, global_variables=None):
		self.loader = loader
		self.roles = roles
		self.variables = variables
		self.states = states
		self.global_variables = global_variables or {}

	@classmethod
	def from_path(cls, root_path, loaders, global_variables=None):
		states = {}
		roles = {}
		variables = {}

		for component in _scan_components(os.path.join(root_path, 'components')):
			roles.update(component.roles)
			states.update(component.states)
			variables.update(component.variables)

		roles.update(_scan(root_path, 'roles', Role))
		variables.update(_scan(root_path, 'variables', Variable))
		states.update(_scan(root_path, 'states', State))

		loader = FileLoader(root_path, loaders)

		return cls(loader, roles, variables, states, global_variables)

	def make_host_env(self, roles, variables, states):
		if roles:
			variables, states = self.merge_roles(roles, variables, states)

		variable_dict = self.global_variables.copy()
		variable_dict.update({v: self.variables[v] for v in variables})
		state_dict = {state: self.states[state] for state in states}

		return HostEnvironment(self.loader, variable_dict, state_dict, self.global_variables)

	def merge_roles(self, roles, variables, states):
		new_variables = {}
		new_states = {}
		for role in roles:
			role = self.loader.load_role(self.roles[role])
			new_variables.update({variable: self.variables[variable] for variable in role.get('variables', [])})
			new_states.update({state: self.states[state] for state in role.get('states', [])})
		new_variables.update(variables)
		new_states.update(states)
		return new_variables, new_states


class HostEnvironment:
	def __init__(self, loader, variables, states, global_variables=None):
		self.loader = loader
		self.states = states
		self.variables = variables
		self.global_variables = global_variables or {}
		self._compiled_variables = None

	@property
	def compiled_variables(self):
		if self._compiled_variables is None:
			tmp_variables = self.global_variables.copy()
			for variable in self.variables.values():
				loaded = self.loader.load_variable(variable, tmp_variables)
				tmp_variables.update(loaded)
			self._compiled_variables = tmp_variables
		return self._compiled_variables

	def get_states(self):
		states = collections.OrderedDict()
		variables = self.compiled_variables
		for state in self.states.values():
			variables['state_file'] = state.name
			states[state.name] = self.loader.load_state(state, variables)
		return states
