import prove.actions


class CmdAction(prove.actions.Action):
	name = 'cmd'

	def run(self):
		result = self.session.run_command(self.args)
		self.session.output.cmd_result(result)


class CmdCommand(prove.actions.Command):
	action_cls = CmdAction
