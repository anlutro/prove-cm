from prove.states.service import systemd, sysv


def running(session, args):
	try:
		return systemd.running(session, args)
	except systemd.SystemdError:
		log.debug('service.systemd.running failed', exc_info=True)

	try:
		return sysv.running(session, args)
	except sysv.SysvError:
		log.debug('service.sysv.running failed', exc_info=True)


def enabled(session, args):
	try:
		return systemd.enabled(session, args)
	except systemd.SystemdError:
		log.debug('service.systemd.enabled failed', exc_info=True)

	try:
		return sysv.enabled(session, args)
	except sysv.SysvError:
		log.debug('service.sysv.enabled failed', exc_info=True)
