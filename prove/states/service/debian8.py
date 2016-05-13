import logging

from prove.states.service import systemd, sysv

LOG = logging.getLogger(__name__)


def running(session, args):
	try:
		return systemd.running(session, args)
	except systemd.SystemdError:
		LOG.debug('service.systemd.running failed', exc_info=True)

	try:
		return sysv.running(session, args)
	except sysv.SysvError:
		LOG.debug('service.sysv.running failed', exc_info=True)


def enabled(session, args):
	try:
		return systemd.enabled(session, args)
	except systemd.SystemdError:
		LOG.debug('service.systemd.enabled failed', exc_info=True)

	try:
		return sysv.enabled(session, args)
	except sysv.SysvError:
		LOG.debug('service.sysv.enabled failed', exc_info=True)
