import yaml
import prove.actions


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
			print(prove.util.indent_string(yaml.dump(session.env.variables, default_flow_style=False), 4))

		if self.inspect_states:
			print('  states:')
			for state in session.env.states:
				print('    ' + state.name + ':')
				for fncall in state.fncalls:
					print('     - fn:', fncall.func)
					for key, value in vars(fncall).items():
						if value and key not in ('func', 'args'):
							print('       {}: {}'.format(key, repr(value)))
					for key, value in fncall.args.items():
						print('       {}: {}'.format(key, repr(value)))
