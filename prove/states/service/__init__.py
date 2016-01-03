def __virtual__(connection):
	os_info = connection.info

	if os_info.distro == 'Debian' and os_info.distro_version >= '8.0':
		import prove.states.service.debian8
		return prove.states.service.debian8

	raise Exception('No appropriate service state module found')
