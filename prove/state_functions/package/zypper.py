from prove.state_functions.package import AbstractPkgState


class ZypperPkgState(AbstractPkgState):
	def _is_installed(self, package):
		result = self.session.run_command('rpm -q {}'.format(package))
		return result.exit_code == 0

	def _install(self, package):
		cmd = ['zypper', 'install', '--no-confirm', package]
		return self.session.run_command(cmd)


def installed(session, args):
	return ZypperPkgState(session).installed(args)
