import importlib
import logging

import prove.actions

log = logging.getLogger(__name__)


class StatesAction(prove.actions.Action):
	name = 'states'

	def run(self, session):
		for state in session.env.states:
			for invocation in state.invocations:
				if invocation.lazy is True:
					log.debug('Skipping lazy invocation: %s %s',
						state.name, invocation.func)
					continue
				session.output.state_invocation_start(state, invocation)
				result = self.run_invocation(invocation, session)
				session.output.state_invocation_finish(state, invocation, result)

	def run_invocation(self, invocation, session):
		if invocation.unless:
			for cmd in invocation.unless:
				if session.run_command(cmd).was_successful:
					return prove.state.StateResult(
						success=True,
						comment='unless command was successful: ' + cmd
					)

		if invocation.onlyif:
			for cmd in invocation.onlyif:
				if not session.run_command(cmd).was_successful:
					return prove.state.StateResult(
						success=True,
						comment='onlyif command failed: ' + cmd
					)

		state_mod, state_func = invocation.func.split('.')
		state_mod = importlib.import_module('prove.states.' + state_mod)

		if hasattr(state_mod, '__virtual__'):
			state_mod = state_mod.__virtual__(session)

		state_func = getattr(state_mod, state_func)
		result = state_func(session, invocation.args)
		if not isinstance(result, prove.state.StateResult):
			raise ValueError('State function {}.{} did not return a StateResult object'.format(
				state_mod.__name__, state_func.__name__))

		if result.changes and invocation.change_listeners:
			for listener in invocation.change_listeners:
				state = session.env.find_state(listener)
				if state:
					for invocation in state.invocations:
						if invocation.lazy:
							invocation.lazy = False

		return result


class StatesCommand(prove.actions.Command):
	action_cls = StatesAction

	def run(self, app):
		if app.options.get('run_until_no_changes'):
			hosts = app.hosts.copy()
			num_changes = -1
			while num_changes != 0:
				num_changes = 0
				for host in hosts:
					with app.executor_connect(host) as session:
						result = self.run_action(session)
						if result.num_states_with_changes == 0:
							hosts.remove(host)
						num_changes += result.num_states_with_changes
		else:
			for host in app.hosts:
				with app.executor_connect(host) as session:
					self.run_action(session)
