import collections

import prove.config


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


class HostEnvironment:
	def __init__(self, options, states, variables):
		assert isinstance(options, prove.config.Options)
		self.options = options
		assert isinstance(states, list)
		self.states = states
		assert isinstance(variables, dict)
		self.variables = variables


class Environment:
	def __init__(self, options, roles, variables, variable_files,
			state_files):
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

		return cls(options=options, roles=roles, variables=variables,
			variable_files=variable_files, state_files=state_files)

	def make_host_env(self, host_config):
		assert isinstance(host_config, prove.config.HostConfig)
		host_variables = self.variables.copy()
		host_options = self.options.make_copy(host_config.options)

		for role in host_config.roles:
			role = self.roles[role]
			for variable_file in role.variable_files:
				host_variables.update(self.variable_files[variable_file].variables)
			host_variables.update(role.variables)
		for variable_file in host_config.variable_files:
			host_variables.update(self.variable_files[variable_file].variables)
		host_variables.update(host_config.variables)

		loaded_states = collections.OrderedDict()
		def load_states(states):
			for state_name in states:
				if state_name in loaded_states:
					continue
				if state_name not in self.state_files:
					raise prove.state.StateMissingException(state_name)
				state = self.state_files[state_name].load(host_variables)
				load_states(state.includes)
				loaded_states[state_name] = state
		for role in host_config.roles:
			load_states(self.roles[role].states)
		load_states(host_config.states)

		for state_name, state in loaded_states.items():
			for required_state_name in state.requires:
				if required_state_name not in loaded_states:
					raise prove.state.StateNotLoadedException(required_state_name, state_name)

		host_states = prove.state.sort_states(loaded_states)

		return HostEnvironment(host_options, host_states, host_variables)
