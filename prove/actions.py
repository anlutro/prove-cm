import prove.state
import importlib


class Action:
	def __init__(self, args):
		self.args = args

	def run(self, app):
		raise NotImplementedError()


class StatesAction(Action):
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
				state_mod, state_fn = invocation.fn.split('.')
				state_mod = importlib.import_module('prove.states.' + state_mod)
				state_fn = getattr(state_mod, state_fn)
				result = state_fn(connection, invocation.args)
				if not isinstance(result, prove.state.StateResult):
					raise ValueError('State function {}.{} did not return a StateResult object'.format(
						state_mod.__name__, state_fn.__name__))
				app.output.state_invocation_finish(state, invocation, result)


class CmdAction(Action):
	def run(self, app):
		for host in app.hosts:
			with app.executor_connect(host) as connection:
				result = connection.run_command(self.args)
				app.output.cmd_result(result)


class PingAction(Action):
	def run(self, app):
		print('PingAction.run')
