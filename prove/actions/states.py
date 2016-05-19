import importlib
import logging

import prove.actions
import prove.states

LOG = logging.getLogger(__name__)


class StatesAction(prove.actions.Action):
	name = 'states'

	def run(self):
		for state in self.session.env.states:
			for invocation in state.invocations:
				if invocation.lazy is True:
					LOG.debug('Skipping lazy invocation: %s %s',
						state.name, invocation.func)
					continue
				self.session.output.state_invocation_start(state, invocation)
				result = self.run_invocation(invocation)
				self.session.output.state_invocation_finish(state, invocation, result)

	def run_invocation(self, invocation):
		if invocation.unless:
			for cmd in invocation.unless:
				if self.session.run_command(cmd).was_successful:
					return prove.states.StateResult(
						success=True,
						comment='unless command was successful: ' + cmd
					)

		if invocation.onlyif:
			for cmd in invocation.onlyif:
				if not self.session.run_command(cmd).was_successful:
					return prove.states.StateResult(
						success=True,
						comment='onlyif command failed: ' + cmd
					)

		state_mod, state_func = invocation.func.split('.')

		# state_function modules have the ability to lazy-load other modules
		# depending on things like linux distribution.
		while isinstance(state_mod, str):
			state_mod = importlib.import_module('prove.state_functions.' + state_mod)
			if hasattr(state_mod, '__virtual__'):
				state_mod = state_mod.__virtual__(self.session)

		state_func = getattr(state_mod, state_func)
		result = state_func(self.session, invocation.args)
		if not isinstance(result, prove.states.StateResult):
			raise ValueError('State function {}.{} did not return a StateResult object'.format(
				state_mod.__name__, state_func.__name__))

		if result.changes and invocation.changes_trigger:
			for listener in invocation.changes_trigger:
				state = self.session.env.find_state(listener)
				if state:
					for invocation in state.invocations:
						if invocation.lazy:
							invocation.lazy = False

		return result


class StatesCommand(prove.actions.Command):
	action_cls = StatesAction

	def run(self, targets=None):
		if targets is None:
			targets = self.app.targets

		if self.app.options.get('run_until_no_changes'):
			self._run_until_no_changes(targets)
		else:
			self._run_once(targets)

	def _run_once(self, targets):
		for target in targets:
			with self.app.executor_connect(target) as session:
				self.run_action(session)

	def _run_until_no_changes(self, targets):
		num_changes = -1
		while num_changes != 0:
			num_changes = 0
			for target in targets:
				with self.app.executor_connect(target) as session:
					result = self.run_action(session)
					if result.num_states_with_changes == 0:
						targets.remove(target)
					num_changes += result.num_states_with_changes
