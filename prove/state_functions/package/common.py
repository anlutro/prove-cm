from prove.states import StateResult


class AbstractPkgState():
	def __init__(self, session):
		self.session = session

	def installed(self, args):
		result = StateResult()

		if self._is_installed(args['package']):
			result.success = True
			result.comment = 'package {} is already installed'.format(args['package'])
			return result

		cmd_result = self._install(args['package'])
		if cmd_result.was_successful:
			result.success = True
			result.comment = 'package {} was installed'.format(args['package'])

		result.success = False
		result.comment = 'package {} could not be installed'.format(args['package'])
		if cmd_result.stderr:
			result.comment += '\n' + cmd_result.stderr
		if cmd_result.stdout:
			result.comment += '\n' + cmd_result.stdout

		return result

	def _is_installed(self, package):
		raise NotImplementedError()

	def _install(self, package):
		raise NotImplementedError()
