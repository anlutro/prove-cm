class StateException(Exception):
	pass


class StateMissingException(StateException):
	msg = 'State "{}" could not be found. Does the state file exist?'
	def __init__(self, state_name):
		super().__init__(self.msg.format(state_name))


class StateNotLoadedException(StateException):
	msg = 'State "{}" (required by "{}") was not found'
	def __init__(self, required_state, requiree_state):
		super().__init__(self.msg.format(required_state, requiree_state))


class StateWrongDataException(StateException):
	msg = 'State "{}" contains bad data - should be a dict'
	def __init__(self, state_name):
		super().__init__(self.msg.format(state_name))


def sort_states(state_files):
	if isinstance(state_files, dict):
		state_files = state_files.values()

	avail_states = {}
	for loaded_state_file in state_files:
		for state in loaded_state_file.states:
			avail_states[state.name] = state

	states = []
	states_added = []
	def append_states(states_to_append):
		for state in states_to_append:
			append_states([avail_states[require] for require in state.requires])
			if state.name in states_added:
				continue
			states.append(state)
			states_added.append(state.name)

	for loaded_state_file in state_files:
		append_states(loaded_state_file.states)

	return states


class StateFile:
	def __init__(self, name, path, loader):
		self.name = name
		self._path = path
		self._loader = loader

	def load(self, variables=None):
		data = self._loader.load(self._path, variables)
		if not isinstance(data, dict):
			raise StateWrongDataException(self.name)

		states = []
		includes = set()
		requires = set()

		for key, value in data.items():
			if key == '_include':
				for include in value:
					includes.add(include)
			elif key == '_require':
				for require in value:
					requires.add(require)
			else:
				invocations = []
				if isinstance(value, dict):
					for func, args in value.items():
						invocations.append(StateInvocation(func, args))
				elif isinstance(value, list):
					for args in value:
						func = args.pop('fn')
						invocations.append(StateInvocation(func, args))
				else:
					raise Exception('State data must be dict or list')
				states.append(State(key, invocations))

		return LoadedStateFile(self.name, states, includes=includes, requires=requires)


class LoadedStateFile:
	def __init__(self, name, states, includes=None, requires=None):
		self.name = name
		self.states = states
		self.includes = includes or set()
		self.requires = requires or set()


class State:
	def __init__(self, name, invocations):
		self.name = name
		self.invocations = invocations

	@property
	def requires(self):
		requires = []
		for invocation in self.invocations:
			if invocation.requires:
				requires += invocation.requires
		return requires


class StateInvocation:
	def __init__(self, func, args):
		self.func = func
		self.requires = args.pop('requires', None)
		self.change_listeners = args.pop('change_listeners', None)
		self.success_listeners = args.pop('success_listeners', None)
		self.failure_listeners = args.pop('failure_listeners', None)
		self.listen_to_changes = args.pop('listen_to_changes', None)
		self.listen_to_success = args.pop('listen_to_success', None)
		self.listen_to_failure = args.pop('listen_to_failure', None)
		lazy_def = self.listen_to_changes or self.listen_to_success or self.listen_to_failure
		self.lazy = args.pop('lazy', lazy_def)
		self.defer = args.pop('defer', False)
		self.args = args


class StateResult:
	def __init__(self, success=None, changes=None, comment=None):
		self.success = success
		self.changes = changes
		self.comment = comment
