from prove.states import State


class upgrade(State):
	def run(self):
		result = self._run_command('apt-get upgrade')
		if result.was_successful:
			return True, result.stdout
		return False, result.stderr


class installed(State):
	def run(self, package=None):
		result = self._run_command('apt-get install -y -q {}'.format(package))
		if result.was_successful:
			return True, result.stdout
		return False, result.stderr
