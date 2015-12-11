from prove.states import State


class Run(State):
	def run(self, command=None, format_vars=None):
		if format_vars is not None:
			command = command.format(**format_vars)
		result = self._run_command(command)
		if result.was_successful:
			return True, result.stdout
		return False, result.stderr
