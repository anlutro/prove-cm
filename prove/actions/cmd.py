import prove.actions


class CmdAction(prove.actions.Action):
	def run(self, app):
		for host in app.hosts:
			with app.executor_connect(host) as connection:
				result = connection.run_command(self.args)
				app.output.cmd_result(result)
