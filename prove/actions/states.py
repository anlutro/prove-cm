import importlib
import logging

import prove.actions
import prove.states

LOG = logging.getLogger(__name__)


class StatesAction(prove.actions.Action):
	name = 'states'

	def run(self):
		for state in self.session.env.states:
			for fncall in state.fncalls:
				if fncall.lazy is True:
					LOG.debug('Skipping lazy fncall: %s %s',
						state.name, fncall.func)
					continue
				self.session.output.state_fncall_start(state, fncall)
				result = self.run_fncall(fncall)
				self.session.output.state_fncall_finish(state, fncall, result)

	def run_fncall(self, fncall):
		if fncall.unless:
			for cmd in fncall.unless:
				if self.session.run_command(cmd).was_successful:
					return prove.states.StateResult(
						success=True,
						comment='unless command was successful: ' + cmd
					)

		if fncall.onlyif:
			for cmd in fncall.onlyif:
				if not self.session.run_command(cmd).was_successful:
					return prove.states.StateResult(
						success=True,
						comment='onlyif command failed: ' + cmd
					)

		state_mod, state_func = fncall.func.split('.')

		# state_function modules have the ability to lazy-load other modules
		# depending on things like linux distribution.
		while isinstance(state_mod, str):
			state_mod = importlib.import_module('prove.state_functions.' + state_mod)
			if hasattr(state_mod, '__virtual__'):
				state_mod = state_mod.__virtual__(self.session)
				if isinstance(state_mod, str):
					state_mod = importlib.import_module(state_mod)

		state_func = getattr(state_mod, state_func)
		result = state_func(self.session, fncall.args)
		if not isinstance(result, prove.states.StateResult):
			raise ValueError('State function {}.{} did not return a StateResult object'.format(
				state_mod.__name__, state_func.__name__))

		if result.changes and fncall.changes_notify:
			for listener in fncall.changes_notify:
				state = self.session.env.find_state(listener)
				if state:
					for fncall in state.fncalls:
						if fncall.lazy:
							fncall.lazy = False

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
