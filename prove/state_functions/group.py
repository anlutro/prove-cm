from prove.states import StateFuncResult


class GroupState():
	def __init__(self, session):
		self.session = session

	def present(self, name, gid=None, system=False):
		result = StateFuncResult()
		if self._group_exists(name):
			result.success = True
			result.comment = 'Group {} already exists'.format(name)
			return result

		cmd = ['addgroup']
		if system:
			cmd.append('--system')
		if gid:
			cmd.append('--gid {}'.format(gid))
		cmd.append(name)

		cmd_result = self.session.run_command(cmd)
		result.success = cmd_result.was_successful
		if result.success:
			result.changes = 'Group {} added'.format(name)
		result.comment = cmd_result.text

		return result

	def absent(self, name):
		result = StateFuncResult()
		if not self._group_exists(name):
			result.success = True
			result.comment = 'Group {} already absent'.format(name)
			return result

		cmd_result = self.session.run_command(['delgroup', name])
		result.success = cmd_result.was_successful
		if result.success:
			result.changes = 'Group {} deleted'.format(name)
		result.comment = cmd_result.text

	def _group_exists(self, name):
		return self.session.run_command('getent group {}'.format(name)).was_successful


def absent(session, args):
	return GroupState(session).absent(**args)


def present(session, args):
	return GroupState(session).present(**args)
