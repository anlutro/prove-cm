def __virtual__(connection):
	os_info = connection.info

	if os_info.distro == 'Debian' or os_info.distro == 'Ubuntu':
		import prove.states.pkg.apt
		return prove.states.pkg.apt

	raise Exception('No appropriate package state module found')
