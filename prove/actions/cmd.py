import prove.actions


class CmdAction(prove.actions.Action):
	name = 'cmd'

	def run(self, session):
		result = session.run_command(self.args)
		session.output.cmd_result(result)


class CmdCommand(prove.actions.Command):
	action_cls = CmdAction
