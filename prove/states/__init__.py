import logging

import prove.util

LOG = logging.getLogger(__name__)


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

	def iter_states():
		for loaded_state_file in state_files:
			for state in loaded_state_file.states:
				yield state

	def append_state(state, stack, only_once=True):
		if state.name in stack:
			raise StateRequireRecursionException(stack + [state.name])

		if only_once and state.name in states_added:
			return

		for require_state in state.requires:
			append_state(avail_states[require_state], stack + [state.name])

		states.append(state)
		states_added.append(state.name)

		for notify_state in state.notify:
			notify_state = avail_states[notify_state]
			if notify_state.defer:
				notify_state._lazy_notified = True
			else:
				append_state(notify_state, stack + [state.name], only_once=False)

	for state in iter_states():
		if not state.lazy and not state.defer:
			append_state(state, [], only_once=True)

	for state in iter_states():
		if state.defer and (not state.lazy or state._lazy_notified):
			append_state(state, [], only_once=True)

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
				funcalls = []
				if isinstance(value, dict):
					for func, args in value.items():
						funcalls.append(StateFuncCall(func, args))
				elif isinstance(value, list):
					for args in value:
						func = args.pop('fn')
						funcalls.append(StateFuncCall(func, args))
				else:
					raise Exception('State data must be dict or list')
				states.append(State(key, funcalls))

		return LoadedStateFile(self.name, states, includes=includes, requires=requires)


class LoadedStateFile:
	def __init__(self, name, states, includes=None, requires=None):
		self.name = name
		self.states = states
		self.includes = includes or set()
		self.requires = requires or set()


class State:
	def __init__(self, name, funcalls):
		self.name = name
		self.funcalls = funcalls
		self.lazy = self._combine_funcall_prop('lazy', bool)
		self.defer = self._combine_funcall_prop('defer', bool)

	def _combine_funcall_prop(self, prop_name, prop_type):
		if prop_type is bool:
			return any([getattr(i, prop_name) for i in self.funcalls])
		elif prop_type is list:
			combined = []
			for i in self.funcalls:
				attr = getattr(i, prop_name)
				if attr:
					combined.extend(attr)
			return combined
		else:
			raise ValueError("don't know how to combine type %s" % prop_type)

	@property
	def notify(self):
		return self._combine_funcall_prop('notify', list)

	@property
	def notify_failure(self):
		return self._combine_funcall_prop('notify_failure', list)

	@property
	def requires(self):
		return self._combine_funcall_prop('requires', list)

	def __repr__(self):
		return '<{} "{}">'.format(self.__class__.__name__, self.name)


class StateFuncCall:
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
		self.notify = _default_list('notify')
		self.notify_failure = _default_list('notify_failure')
		self.listen = _default_list('listen')
		self.listen_failure = _default_list('listen_failure')

		# if lazy isn't defined, default to true if any of the "listens" are set
		self.lazy = args.pop('lazy', self.listen or self.listen_failure)
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
