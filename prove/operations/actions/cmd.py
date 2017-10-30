import prove.operations


class CmdAction(prove.operations.Action):
	name = 'cmd'

	def run(self):
		result = self.session.run_command(self.args)
		self.session.output.cmd_result(result)
