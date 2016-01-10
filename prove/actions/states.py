import importlib

import prove.actions


class StatesAction(prove.actions.Action):
	def run(self, app):
		if app.options.get('run_until_no_changes'):
			num_changes = -1
			while num_changes != 0:
				num_changes = 0
				for host in app.hosts:
					with app.executor_connect(host) as session:
						result = self.run_states(app, host, session)
						if result.num_states_with_changes == 0:
							app.hosts.remove(host)
							num_changes += result.num_states_with_changes
		else:
			for host in app.hosts:
				with app.executor_connect(host) as session:
					self.run_states(app, host, session)

	def run_states(self, app, host, session):
		for state in session.env.states:
			for invocation in state.invocations:
				app.output.state_invocation_start(state, invocation)
				result = self.run_invocation(invocation, session)
				app.output.state_invocation_finish(state, invocation, result)

	def run_invocation(self, invocation, session):
		state_mod, state_func = invocation.func.split('.')
		state_mod = importlib.import_module('prove.states.' + state_mod)

		if hasattr(state_mod, '__virtual__'):
			state_mod = state_mod.__virtual__(session)

		state_func = getattr(state_mod, state_func)
		result = state_func(session, invocation.args)
		if not isinstance(result, prove.state.StateResult):
			raise ValueError('State function {}.{} did not return a StateResult object'.format(
				state_mod.__name__, state_func.__name__))
		return result
