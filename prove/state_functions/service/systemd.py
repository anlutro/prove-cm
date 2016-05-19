import logging

from prove.state_functions.service import ServiceState

LOG = logging.getLogger(__name__)


class SystemdError(Exception):
	pass


class SystemdServiceState(ServiceState):
	def is_service_running(self, session, service):
		result = session.run_command('systemctl show {}'.format(service))
		if 'ActiveState=active' in result.stdout:
			is_running = True
		elif 'ActiveState=inactive' in result.stdout:
			is_running = False
		else:
			raise Exception('Could not parse `systemctl show` output')
		return is_running

	def start_service(self, session, service):
		return session.run_command('systemctl start {}'.format(service))

	def is_service_enabled(self, session, service):
		result = session.run_command('systemctl is-enabled {}'.format(service))
		if result.exit_code == 0:
			return True
		elif result.exit_code == 1:
			return False
		else:
			raise SystemdError(result.stderr or result.stdout)

	def enable_service(self, session, service):
		return session.run_command('systemctl enable {}'.format(service))


def running(session, args):
	return SystemdServiceState().running(session, args)


def enabled(session, args):
	return SystemdServiceState().enabled(session, args)
