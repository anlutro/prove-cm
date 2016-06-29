import prove.actions


class TestAction(prove.actions.Action):
	name = 'test'

	def run(self):
		raise RuntimeError('Test error')


class TestCommand(prove.actions.Command):
	action_cls = TestAction
