import prove.operations


class TestAction(prove.operations.Action):
	name = 'test'

	def run(self):
		if self.args:
			if self.args[0] == 'error' or self.args[0] == 'exception':
				raise RuntimeError('Test error')

		self.session.output.comment('test reply')


class TestCommand(prove.operations.Command):
	action_cls = TestAction
