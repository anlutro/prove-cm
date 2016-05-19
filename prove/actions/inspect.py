import yaml
import prove.actions


def _indent(string, spaces):
	return '\n'.join((((' ' * spaces) + line) for line in string.splitlines()))


class InspectCommand(prove.actions.Command):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.inspect_simple_things = True
		self.inspect_variables = 'variables' in self.args
		self.inspect_states = 'states' in self.args
		if 'all' in self.args or 'everything' in self.args:
			self.inspect_variables = True
			self.inspect_states = True
		if self.inspect_variables or self.inspect_states:
			self.inspect_simple_things = False

	def run_target(self, target):
		session = self.app.make_session(target)

		print(target.name + ':')

		if self.inspect_simple_things:
			if target.host != target.name:
				print('  host:', target.host)
			if target.roles:
				print('  roles:', ', '.join(target.roles))
			if target.groups:
				print('  groups:', ', '.join(target.groups))

		if self.inspect_variables:
			print('  variables:')
			print(_indent(yaml.dump(session.env.variables, default_flow_style=False), 4))

		if self.inspect_states:
			print('  states:')
			for state in session.env.states:
				print('    ' + state.name + ':')
				for invocation in state.invocations:
					print('     - fn:', invocation.func)
					for key, value in vars(invocation).items():
						if value and key not in ('func', 'args'):
							print('       {}: {}'.format(key, repr(value)))
					for key, value in invocation.args.items():
						print('       {}: {}'.format(key, repr(value)))