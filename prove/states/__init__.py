import prove.util


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


class StateRequireRecursionException(StateException):
	def __init__(self, stack):
		stack_str = ' -> '.join(stack)
		super().__init__('State requirement recursion detected: ' + stack_str)


def sort_states(state_files):
	if isinstance(state_files, dict):
		state_files = state_files.values()

	avail_states = {}
	for loaded_state_file in state_files:
		for state in loaded_state_file.states:
			avail_states[state.name] = state

	states = []
	states_added = []

	def append_states(states_to_append, stack):
		for state in states_to_append:
			if state.name in stack:
				raise StateRequireRecursionException(stack + [state.name])

			append_states(
				[avail_states[require] for require in state.requires],
				stack + [state.name]
			)

			if state.name in states_added:
				continue

			states.append(state)
			states_added.append(state.name)

	for loaded_state_file in state_files:
		append_states(loaded_state_file.states, [])

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

	def __repr__(self):
		return '<{} "{}">'.format(self.__class__.__name__, self.name)


class StateInvocation:
	def __init__(self, func, args):
		self.func = func

		def _default_list(name):
			arg = args.pop(name, None)
			if arg is not None and not isinstance(arg, list):
				arg = [arg]
			return arg

		self.requires = _default_list('requires')
		self.unless = _default_list('unless')
		self.onlyif = _default_list('onlyif')
		self.changes_trigger = _default_list('changes_trigger')
		self.success_trigger = _default_list('success_trigger')
		self.failure_trigger = _default_list('failure_trigger')
		self.listen_changes = _default_list('listen_changes')
		self.listen_success = _default_list('listen_success')
		self.listen_failure = _default_list('listen_failure')

		lazy_def = self.listen_changes or self.listen_success or self.listen_failure
		self.lazy = args.pop('lazy', lazy_def)
		self.defer = args.pop('defer', False)
		self.args = args


class StateResult:
	def __init__(self, success=None, changes=None, comment=None, comments=None,
			stdout=None, stderr=None):
		self.success = success
		self.changes = changes
		self.comment = comment
		self.comments = comments
		self.stdout = stdout
		self.stderr = stderr

	def format_comment(self):
		comment = self.comment or ''

		if self.comments:
			comment += '\n' + '\n'.join(self.comments)

		if self.stdout:
			comment += '\n\nSystem stdout:\n' + prove.util.indent_string(self.stdout, 2)

		if self.stderr:
			comment += '\n\nSystem stderr:\n' + prove.util.indent_string(self.stderr, 2)

		return comment.strip()
