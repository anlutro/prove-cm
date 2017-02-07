def __virtual__(session):
	distro = session.info.distro.lower()

	if distro == 'debian' or distro == 'ubuntu':
		import prove.state_functions.package.apt
		return prove.state_functions.package.apt
	elif distro.startswith('opensuse'):
		import prove.state_functions.package.zypper
		return prove.state_functions.package.zypper

	raise Exception('No appropriate package state module found')
