from prove.state import StateResult


class AptError(Exception):
	pass


def _is_installed(session, package):
	result = session.run_command('dpkg -s {}'.format(package))
	return result.exit_code == 0


def _install(session, package):
	cmd = ('apt-get'
		'-o DPkg::Options::=--force-confnew'
		'-o DPkg::Options::=--force-confdef'
		'--assume-yes install {pkg}')
	cmd = cmd.format(pkg=package)
	return session.run_command(cmd)


def installed(session, args):
	result = StateResult()

	if _is_installed(session, args['package']):
		result.success = True
		result.comment = 'Package {} is already installed'.format(args['package'])
		return result

	cmd_result = _install(session, args['package'])
	if cmd_result.was_successful:
		result.success = True
		result.comment = 'Package {} was installed'.format(args['package'])

	result.success = False
	result.comment = 'Package {} could not be installed'.format(args['package'])
	if cmd_result.stderr:
		result.comment += '\n' + cmd_result.stderr
	if cmd_result.stdout:
		result.comment += '\n' + cmd_result.stdout
	return result
