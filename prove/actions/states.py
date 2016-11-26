import importlib
import logging

import prove.actions
import prove.states

LOG = logging.getLogger(__name__)


class StatesAction(prove.actions.Action):
	name = 'states'

	def run(self):
		for state in self.session.env.states:
			for funcall in state.funcalls:
				if funcall.lazy is True:
					LOG.debug('Skipping lazy funcall: %s %s',
						state.name, funcall.func)
					continue
				self.session.output.state_funcall_start(state, funcall)
				result = self.run_funcall(funcall)
				self.session.output.state_funcall_finish(state, funcall, result)

	def run_funcall(self, funcall):
		if funcall.unless:
			for cmd in funcall.unless:
				if self.session.run_command(cmd).was_successful:
					return prove.states.StateResult(
						success=True,
						comment='unless command was successful: ' + cmd
					)

		if funcall.onlyif:
			for cmd in funcall.onlyif:
				if not self.session.run_command(cmd).was_successful:
					return prove.states.StateResult(
						success=True,
						comment='onlyif command failed: ' + cmd
					)

		state_mod, state_func = funcall.func.split('.')

		# state_function modules have the ability to lazy-load other modules
		# depending on things like linux distribution.
		while isinstance(state_mod, str):
			state_mod = importlib.import_module('prove.state_functions.' + state_mod)
			if hasattr(state_mod, '__virtual__'):
				state_mod = state_mod.__virtual__(self.session)

		state_func = getattr(state_mod, state_func)
		result = state_func(self.session, funcall.args)
		if not isinstance(result, prove.states.StateResult):
			raise ValueError('State function {}.{} did not return a StateResult object'.format(
				state_mod.__name__, state_func.__name__))

		if result.changes and funcall.changes_notify:
			for listener in funcall.changes_notify:
				state = self.session.env.find_state(listener)
				if state:
					for funcall in state.funcalls:
						if funcall.lazy:
							funcall.lazy = False

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
