import collections
import logging
from lazy import lazy

import prove.util

LOG = logging.getLogger(__name__)


class StateException(Exception):
	pass


class StateMissingException(StateException):
	msg = 'State %r could not be found.'
	def __init__(self, state_name):
		super().__init__(self.msg % (state_name))


class StateDependencyMissingException(StateException):
	msg = 'Dependency %r for state %r could not be found.'
	def __init__(self, state, required_state):
		super().__init__(self.msg % (required_state, state))


class StateFileMissingException(StateException):
	msg = 'State file "{}" could not be found. Does the state file exist?'
	def __init__(self, state_file_name):
		super().__init__(self.msg.format(state_file_name))


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


def get_states(state_files):
	states = []

	for loaded_state_file in state_files.values():
		for state in loaded_state_file.states:
			states.append(state)

	return StateCollection(states)


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
				fncalls = []
				if isinstance(value, dict):
					for func, args in value.items():
						fncalls.append(StateFuncCall(func, args))
				elif isinstance(value, list):
					for args in value:
						func = args.pop('fn')
						fncalls.append(StateFuncCall(func, args))
				else:
					raise Exception('State data must be dict or list')
				states.append(State(key, fncalls))

		return LoadedStateFile(self.name, states, includes=includes, requires=requires)


class LoadedStateFile:
	def __init__(self, name, states, includes=None, requires=None):
		self.name = name
		self.states = states
		self.includes = includes or set()
		self.requires = requires or set()


class StateMap:
	def __init__(self, data=None):
		if isinstance(data, list):
			data = {s.name: s for s in data}
		elif isinstance(data, dict):
			data = {state.name: value for state, value in data.items()}
		self.states = data or {}

	def __contains__(self, key):
		if isinstance(key, State):
			key = key.name
		return key in self.states

	def __getitem__(self, key):
		if isinstance(key, State):
			key = key.name
		return self.states[key]

	def __setitem__(self, key, value):
		if isinstance(key, State):
			key = key.name
		self.states[key] = value

	def __iter__(self):
		return self.states

	def __len__(self):
		return len(self.states)

	def __repr__(self):
		return repr(self.states)


class StateCollection:
	def __init__(self, states):
		self.states = states
		self.states_map = StateMap(states)

	def __iter__(self):
		return self.states

	def __getitem__(self, key):
		return self.states_map[key]

	@lazy
	def root_states(self):
		return [state for state in self.states if state.is_valid_root]

	@lazy
	def depends(self):
		dependencies = collections.defaultdict(lambda: [])

		for state in self.states:
			for required_state in state.requires:
				try:
					dependencies[state].append(self[required_state])
				except KeyError as e:
					raise StateDependencyMissingException(state, required_state) from e

		return StateMap(dependencies)

	@lazy
	def rdepends(self):
		rev_dependencies = collections.defaultdict(lambda: [])

		for state in self.states:
			for required_state in state.requires:
				try:
					rev_dependencies[self[required_state]].append(state)
				except KeyError as e:
					raise StateDependencyMissingException(state, required_state) from e

		return StateMap(rev_dependencies)


class State:
	def __init__(self, name, fncalls):
		self.name = name
		self.fncalls = fncalls
		self.lazy = self._combine_fncall_prop('lazy', bool)
		self.defer = self._combine_fncall_prop('defer', bool)

	def _combine_fncall_prop(self, prop_name, prop_type):
		if prop_type is bool:
			return any([getattr(fncall, prop_name) for fncall in self.fncalls])
		elif prop_type is list:
			combined = []
			for fncall in self.fncalls:
				attr = getattr(fncall, prop_name)
				if attr:
					combined.extend(attr)
			return combined
		else:
			raise ValueError("don't know how to combine type %s" % prop_type)

	@property
	def notify(self):
		return self._combine_fncall_prop('notify', list)

	@property
	def notify_failure(self):
		return self._combine_fncall_prop('notify_failure', list)

	@property
	def requires(self):
		return self._combine_fncall_prop('requires', list)

	@property
	def is_valid_root(self):
		return not self.requires and not self.lazy and not self.defer

	def __repr__(self):
		return '<{} "{}">'.format(self.__class__.__name__, self.name)

	def __gt__(self, other):
		return self.name > other.name


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

	@property
	def main_arg(self):
		args_list = list(self.args.values())
		if args_list:
			return args_list[0]
		return None

	def __repr__(self):
		return '<{} "{}">'.format(self.__class__.__name__, self.func)


class StateResult:
	def __init__(self, success, func_results):
		self.success = success
		self.func_results = func_results


class StateFuncResult:
	def __init__(self, success=None, changes=None, comment=None, comments=None,
			stdout=None, stderr=None):
		self.success = success
		self.changes = changes
		self.comment = comment
		self.comments = comments
		self.stdout = stdout
		self.stderr = stderr

	@property
	def failure(self):
		return not self.success

	def format_comment(self):
		return prove.util.format_result(
			comment=self.comment,
			comments=self.comments,
			stdout=self.stdout,
			stderr=self.stderr,
		)

	def merge_with_cmd_result(self, cmd_result):
		self.success = cmd_result.was_successful
		self.stdout = cmd_result.stdout
		self.stderr = cmd_result.stderr


class StateInvocation:
	def __init__(self, state):
		self.state = state

	@property
	def fncalls(self):
		return self.state.fncalls


class LazyStateInvocation:
	def __init__(self, state):
		assert state.lazy
		self.state = state
		self._lazy_notified = False
