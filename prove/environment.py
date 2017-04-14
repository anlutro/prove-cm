import collections

import prove.config
import prove.states


class Role:
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


class VariableFile:
	def __init__(self, name, variables):
		self.name = name
		self.variables = variables


class TargetEnvironment:
	def __init__(self, options, states, variables, files):
		if isinstance(options, dict):
			options = prove.config.Options(options)
		assert isinstance(options, prove.config.Options)
		self.options = options

		if isinstance(states, list):
			states = prove.states.StateCollection(states)
		assert isinstance(states, prove.states.StateCollection)
		self.states = states

		assert isinstance(variables, dict)
		self.variables = variables

		assert isinstance(files, dict)
		self.files = files


class Environment:
	def __init__(self, options, roles, variables, variable_files, state_files, files):
		assert isinstance(options, prove.config.Options)
		self.options = options
		assert isinstance(roles, dict)
		self.roles = roles
		assert isinstance(variables, dict)
		self.variables = variables
		assert isinstance(variable_files, dict)
		self.variable_files = variable_files
		assert isinstance(state_files, dict)
		self.state_files = state_files
		assert isinstance(files, dict)
		self.files = files

	@classmethod
	def from_options_and_config(cls, options, config):
		roles = collections.OrderedDict({
			name: Role.from_dict(name, data)
			for name, data in config.get('roles', {}).items()
		})

		variables = config.get('variables', {})

		from prove.loaders import json, yaml, yaml_mako
		loaders = [json, yaml, yaml_mako]

		locator = prove.locator.Locator(
			options['root_dir'],
			loaders
		)

		roles.update(locator.locate_roles())
		variable_files = locator.locate_variables()
		state_files = locator.locate_states()
		files = locator.locate_files()

		for component in locator.locate_components().values():
			roles.update(component.roles)
			variable_files.update(component.variable_files)
			state_files.update(component.state_files)
			files.update(component.files)

		return cls(options=options, roles=roles, variables=variables,
			variable_files=variable_files, state_files=state_files, files=files)

	def make_target_env(self, target):
		assert isinstance(target, prove.config.Target)
		tgt_variables = self.variables.copy()
		tgt_options = self.options.make_copy(target.options)

		for role in target.roles:
			role = self.roles[role]
			for variable_file in role.variable_files:
				tgt_variables.update(self.variable_files[variable_file].variables)
			tgt_variables.update(role.variables)
		for variable_file in target.variable_files:
			tgt_variables.update(self.variable_files[variable_file].variables)
		tgt_variables.update(target.variables)

		loaded_state_files = collections.OrderedDict()
		def load_state_files(state_files):
			for state_file in state_files:
				if state_file in loaded_state_files:
					continue
				if state_file not in self.state_files:
					raise prove.states.StateFileMissingException(state_file)
				state = self.state_files[state_file].load(tgt_variables)
				load_state_files(state.includes)
				loaded_state_files[state_file] = state
		for role in target.roles:
			load_state_files(self.roles[role].states)
		load_state_files(target.states)

		for file_name, state_file in loaded_state_files.items():
			for required_file_name in state_file.requires:
				if required_file_name not in loaded_state_files:
					raise prove.states.StateNotLoadedException(required_file_name, file_name)

		tgt_states = prove.states.get_states(loaded_state_files)

		return TargetEnvironment(tgt_options, tgt_states, tgt_variables, self.files)
