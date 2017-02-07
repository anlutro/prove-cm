from prove.state_functions.package.common import AbstractPkgState


class AptPkgState(AbstractPkgState):
	def _is_installed(self, package):
		result = self.session.run_command('dpkg -s {}'.format(package))
		return result.exit_code == 0

	def _install(self, package):
		cmd = [
			'apt-get', 'install', pkg, '--assume-yes',
			'-o', 'DPkg::Options::=--force-confnew',
			'-o', 'DPkg::Options::=--force-confdef',
			'-o', 'DPkg::Options::=--force-confmiss',
		]
		return self.session.run_command(cmd)


def installed(session, args):
	return AptPkgState(session).installed(args)
