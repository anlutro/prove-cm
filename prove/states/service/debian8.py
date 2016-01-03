from prove.states.service import systemd, sysv


def running(connection, args):
	try:
		return systemd.running(connection, args)
	except systemd.SystemdError:
		log.debug('service.systemd.running failed', exc_info=True)

	try:
		return sysv.running(connection, args)
	except sysv.SysvError:
		log.debug('service.sysv.running failed', exc_info=True)


def enabled(connection, args):
	try:
		return systemd.enabled(connection, args)
	except systemd.SystemdError:
		log.debug('service.systemd.enabled failed', exc_info=True)

	try:
		return sysv.enabled(connection, args)
	except sysv.SysvError:
		log.debug('service.sysv.enabled failed', exc_info=True)
