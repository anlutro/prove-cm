from prove.state import StateResult


class GroupState():
	def __init__(self, session):
		self.session = session

	def present(self, name, gid=None, system=False):
		result = StateResult()
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

	def _group_exists(self, name):
		return self.session.run_command('getent group {}'.format(name)).was_successful

def present(session, args):
	return GroupState(session).present(**args)
