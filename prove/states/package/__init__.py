def __virtual__(session):
	os_info = session.info

	if os_info.distro == 'Debian' or os_info.distro == 'Ubuntu':
		import prove.states.package.apt
		return prove.states.package.apt

	raise Exception('No appropriate package state module found')
