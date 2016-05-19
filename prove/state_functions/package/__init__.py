def __virtual__(session):
	os_info = session.info

	if os_info.distro == 'Debian' or os_info.distro == 'Ubuntu':
		import prove.state_functions.package.apt
		return prove.state_functions.package.apt

	raise Exception('No appropriate package state module found')
