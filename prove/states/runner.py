from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import importlib
import logging

from prove.states import StateResult
from prove.states.graph import generate_graph

LOG = logging.getLogger(__name__)


class StateRunner:
	def __init__(self, session, states=None, output=None):
		self.session = session
		self.states = states or session.env.states
		self.output = output or session.output
		self.results = {}

	def run(self):
		for state in self.states:
			self.run_state(state)

		LOG.debug('finished running states')

		return self.results

	def get_state_function(self, func):
		state_mod, state_func = func.split('.')

		# state_function modules have the ability to lazy-load other modules
		# depending on things like linux distribution.
		while isinstance(state_mod, str):
			state_mod = state_mod.replace('prove.state_functions.', '')
			state_mod = importlib.import_module('prove.state_functions.' + state_mod)
			if hasattr(state_mod, '__virtual__'):
				state_mod = state_mod.__virtual__(self.session)

		return getattr(state_mod, state_func)

	def run_state(self, state):
		LOG.debug('running state %r', state)

		if state in self.results:
			raise Exception('state %r already in results!' % state)

		self.session.output.state_start(state)
		self.results[state] = {}
		ret = True

		for fncall in state.fncalls:
			LOG.debug('running state.fncall %r', fncall)
			self.session.output.state_fncall_start(state, fncall)

			prereq_result = self.state_prereqs(fncall)
			if prereq_result:
				result = prereq_result
			else:
				state_func = self.get_state_function(fncall.func)
				result = state_func(self.session, fncall.args)

				if not isinstance(result, StateResult):
					raise ValueError('State function {}.{} did not return a StateResult object'.format(
						state_func.__mod__.__name__, state_func.__name__))

			LOG.debug('finished state.fncall %r', fncall)
			self.session.output.state_fncall_finish(state, fncall, result)
			self.results[state][fncall] = result

			if result.failure:
				ret = False
				if fncall.notify_failure:
					for notify_state in fncall.notify_failure:
						self.run_state(notify_state)
				LOG.info('state.fncall %r failed, aborting', fncall)
				break

			if result.success and result.changes and fncall.notify:
				for notify_state in fncall.notify:
					self.run_state(notify_state)

		return ret

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
				msg = 'prerequisite met: %s: %s' % (
					('success' if expect_success else 'failure'),
					cmd
				)
				return StateResult(success=True, comment=msg)


class ParallelizedStateRunner(StateRunner):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.graph = generate_graph(self.states)

	def run(self, parallelism=1):
		def run_node_wrapper(node):
			try:
				self.run_node(node)
			except: # pylint: disable=bare-except
				LOG.exception('exception occured while running node %r', node)

		LOG.debug('running states with parallelism %d', parallelism)
		with ThreadPoolExecutor(max_workers=parallelism) as pool:
			for root_node in self.graph.roots:
				pool.submit(run_node_wrapper, root_node)
		LOG.debug('finished running states')

		return self.results

	def run_node(self, node):
		for state in node.states:
			if not self.run_state(state):
				LOG.info('state %r failed, aborting', state)
				return False
		if node.children:
			for child_node in node.children:
				if not self.run_node(child_node):
					LOG.info('child node %r failed, aborting', child_node)
					return False
