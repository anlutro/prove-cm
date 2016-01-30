import logging

from prove.states.service import ServiceState

log = logging.getLogger(__name__)


class SysvError(Exception):
	pass


class SysvServiceState(ServiceState):
	def is_service_running(self, session, service):
		result = session.run_command('service {} status'.format(service))
		if result.exit_code == 3:
			return False
		elif result.exit_code == 0:
			return True
		raise SysvError('Unknown exit code: {}'.format(result.exit_code))

	def start_service(self, session, service):
		return session.run_command('service {} start'.format(service))

	def is_service_enabled(self, session, service):
		result = session.run_command('chkconfig {}'.format(service))
		if result.exit_code == 127:
			log.warning('Could not determine if service is enabled because chkconfig'
				' is not installed or is not in $PATH.')
			return False
		if result.stdout.endswith('on'):
			return True
		elif result.stdout.endswith('off'):
			return False
		raise SysvError('Could not parse chkconfig stdout')

	def enable_service(self, session, service):
		result = session.run_command('chkconfig {} on'.format(service))
		if result.exit_code == 127:
			log.warning('Could not determine if service is enabled because chkconfig'
				' is not installed or is not in $PATH.')
		return result


def running(session, args):
	return SysvServiceState().running(session, args)


def enabled(session, args):
	return SysvServiceState().enabled(session, args)
