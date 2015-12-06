from prove.states import State


class run(State):
	def run(self, command=None, format_vars=None):
		if format_vars is None: format_vars = {}
		result = self._run_command(command.format(**format_vars))
		if result.was_successful:
			return True, result.stdout
		return False, result.stderr
