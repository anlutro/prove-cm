from prove.catalog.states import StateFuncResult


def __virtual__(session):
	os_info = session.info

	if os_info.distro == 'Debian' and os_info.distro_version >= '8.0':
		return 'service.debian8'
	elif session.info.program_exists('systemctl'):
		return 'service.systemd'

	raise Exception('No appropriate service state module found')


class ServiceState():
	def enabled(self, session, args):
		result = StateFuncResult()

		if self.is_service_enabled(session, args['service']):
			result.success = True
			result.comment = 'service {} is already enabled'.format(args['service'])
			return result

		cmd_result = self.enable_service(session, args['service'])
		if cmd_result.was_successful:
			result.success = True
			result.comment = 'service {} was enabled'.format(args['service'])
			return result

		result.success = False
		result.comment = 'service {} could not be enabled'.format(args['service'])
		if cmd_result.stderr:
			result.comment += '\n' + cmd_result.stderr
		if cmd_result.stdout:
			result.comment += '\n' + cmd_result.stdout
		return result

	def running(self, session, args):
		result = StateFuncResult()

		if self.is_service_running(session, args['service']):
			result.success = True
			result.comment = 'service {} is already running'.format(args['service'])
			return result

		cmd_result = self.start_service(session, args['service'])
		if cmd_result.was_successful:
			result.success = True
			result.comment = 'service {} was started'.format(args['service'])
			return result

		result.success = False
		result.comment = 'service {} could not be started'.format(args['service'])
		if cmd_result.stderr:
			result.comment += '\n' + cmd_result.stderr
		if cmd_result.stdout:
			result.comment += '\n' + cmd_result.stdout
		return result

	def is_service_running(self, session, service):
		raise NotImplementedError()

	def start_service(self, session, service):
		raise NotImplementedError()

	def is_service_enabled(self, session, service):
		raise NotImplementedError()

	def enable_service(self, session, service):
		raise NotImplementedError()
