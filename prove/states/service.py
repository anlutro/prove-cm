from prove.states import State


class Running(State):
	def run(self, service=None):
		result = self._run_command('systemctl status {}'.format(service))
		if result.was_successful:
			return True, 'Service {} is already running'.format(service)

		result = self._run_command('systemctl start {}'.format(service))
		if result.was_successful:
			return True, result.stdout or 'Service {} was started'.format(service)
		return False, result.stderr or 'Service {} could not be started'.format(service)


class Enabled(State):
	def run(self, service=None):
		result = self._run_command('systemctl is-enabled {}'.format(service))
		if result.was_successful:
			return True, 'Service {} is already enabled'.format(service)

		result = self._run_command('systemctl enable {}'.format(service))
		if result.was_successful:
			return True, result.stdout or 'Service {} was enabled'.format(service)
		return False, result.stderr or 'Service {} could not be enabled'.format(service)
