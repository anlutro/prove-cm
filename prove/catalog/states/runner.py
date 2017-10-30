import importlib
import logging

import prove.catalog.states

LOG = logging.getLogger(__name__)


class StateRunException(Exception):
	pass


def run_states(session, parallelism=None):
	runner = StatesRunner(session)
	return runner.run()


class AbstractStateRunner:
	def __init__(self, session, output=None):
		self.session = session
		self.output = output or session.output
		self.results = []

	def get_state_function(self, func):
		state_mod, state_func = func.split('.')

		# state_function modules have the ability to lazy-load other modules
		# depending on things like linux distribution.
		while isinstance(state_mod, str):
			state_mod = state_mod.replace('prove.state_functions.', '')
			try:
				state_mod = importlib.import_module('prove.state_functions.' + state_mod)
			except ImportError as e:
				raise StateRunException('no state_functions module %r' % state_mod) from e
			if hasattr(state_mod, '__virtual__'):
				state_mod = state_mod.__virtual__(self.session)

		if not hasattr(state_mod, state_func):
			raise StateRunException('module %r has no function %r' % (state_mod, state_func))

		return getattr(state_mod, state_func)

	def run_state(self, state):
		LOG.debug('running state %r', state)
		self.session.output.state_start(state)

		success = True
		func_results = []
		for fncall in state.fncalls:
			func_result = self.run_fncall(state, fncall)
			func_results.append((fncall, func_result))
			func_results.extend(self.on_fncall_result(fncall, func_result))
			if not func_result.success:
				success = False
				LOG.info('state %r fncall %r failed, aborting', state, fncall)
				break

		state_result = prove.catalog.states.StateResult(success, func_results)
		LOG.debug('finished state %r', state)
		self.session.output.state_finish(state, state_result)

		self.results.append((state, state_result))
		self.on_state_result(state, state_result)

	def run_fncall(self, state, fncall):
		LOG.debug('running state.fncall %r', fncall)
		self.session.output.state_fncall_start(state, fncall)

		prereq_result = self.state_prereqs(fncall)
		if prereq_result:
			result = prereq_result
		else:
			state_func = self.get_state_function(fncall.func)
			result = state_func(self.session, fncall.args)

			if not isinstance(result, prove.catalog.states.StateFuncResult):
				raise ValueError('State function {}.{} did not return a StateFuncResult object'.format(
					state_func.__mod__.__name__, state_func.__name__))

		LOG.debug('finished state.fncall %r', fncall)
		self.session.output.state_fncall_finish(state, fncall, result)

		return result

	def state_prereqs(self, fncall):
		result = None
		if fncall.onlyif:
			result = self.state_prereq(fncall.onlyif, True)
		if not result and fncall.unless:
			result = self.state_prereq(fncall.unless, False)
		return result

	def state_prereq(self, commands, expect_success):
		for cmd in commands:
			if self.session.run_command(cmd).was_successful == expect_success:
				msg = 'prerequisite met: %s: %r' % (
					('success' if expect_success else 'failure'),
					cmd
				)
				return prove.catalog.states.StateFuncResult(success=True, comment=msg)

	def on_fncall_result(self, fncall, result):
		return []

	def on_state_result(self, state, result):
		pass


class SingleStateRunner(AbstractStateRunner):
	def run(self, state):
		for fncall in state.fncalls:
			self.run_fncall(state, fncall)
		return self.results


class StatesRunner(AbstractStateRunner):
	def __init__(self, session, states=None, output=None):
		super().__init__(session, output=output)
		self.states = states or session.env.states
		assert isinstance(self.states, prove.catalog.states.StateCollection), self.states
		self.deferred = []

	def get_state(self, state_name):
		for state in self.states:
			if state.name == state_name:
				return state
		return None

	def run(self):
		self.deferred = []

		LOG.debug('running %d root states', len(self.states.root_states))
		for state in self.states.root_states:
			self.run_state(state)

		LOG.debug('running %d deferred states', len(self.deferred))
		while self.deferred:
			for state in self.deferred:
				self.run_state(state)

	def on_fncall_result(self, fncall, result):
		results = []

		def run_notify_states(states):
			for state in states:
				nofity_result = self.run_notify_state(state)
				if nofity_result:
					results.append((state, nofity_result))

		if result.failure and fncall.notify_failure:
			run_notify_states(fncall.notify_failure)

		if result.success and result.changes and fncall.notify:
			run_notify_states(fncall.notify)

		return results

	def run_notify_state(self, state_name):
		state = self.get_state(state_name)
		if state.defer:
			self.deferred.append(state)
			return None
		return self.run_state(state)

	def on_state_result(self, state, result):
		if not result.success:
			return

		if state in self.states.rdepends:
			for rdep_state in self.states.rdepends[state]:
				LOG.debug('state %r depends on %r. running it', rdep_state, state)
				self.run_state(rdep_state)
