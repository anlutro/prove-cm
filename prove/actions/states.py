import importlib

import prove.actions


class StatesAction(prove.actions.Action):
	def run(self, app):
		if app.options.get('run_until_no_changes'):
			num_changes = -1
			while num_changes != 0:
				num_changes = 0
				for host in app.hosts:
					with app.executor_connect(host) as connection:
						result = self.run_states(app, host, connection)
						if result.num_states_with_changes == 0:
							app.hosts.remove(host)
							num_changes += result.num_states_with_changes
		else:
			for host in app.hosts:
				with app.executor_connect(host) as connection:
					self.run_states(app, host, connection)

	def run_states(self, app, host, connection):
		for state in connection.env.states:
			for invocation in state.invocations:
				app.output.state_invocation_start(state, invocation)
				result = self.run_invocation(invocation, connection)
				app.output.state_invocation_finish(state, invocation, result)

	def run_invocation(self, invocation, connection):
		state_mod, state_fn = invocation.fn.split('.')
		state_mod = importlib.import_module('prove.states.' + state_mod)

		if hasattr(state_mod, '__virtual__'):
			state_mod = state_mod.__virtual__(connection)

		state_fn = getattr(state_mod, state_fn)
		result = state_fn(connection, invocation.args)
		if not isinstance(result, prove.state.StateResult):
			raise ValueError('State function {}.{} did not return a StateResult object'.format(
				state_mod.__name__, state_fn.__name__))
		return result
