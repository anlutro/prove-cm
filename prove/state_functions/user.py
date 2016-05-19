from prove.states import StateResult


class UserState():
	def __init__(self, session):
		self.session = session

	def present(self, name, uid=None, gid=None, system=False, home=None):
		result = StateResult()
		if self._user_exists(name):
			result.success = True
			result.comment = 'User {} already exists'.format(name)
			return result

		cmd = ['adduser']
		if system:
			cmd.append('--system')
		if uid:
			cmd.append('--uid {}'.format(uid))
		if gid:
			cmd.append('--gid {}'.format(gid))
		cmd.append(name)

		cmd_result = self.session.run_command(cmd)
		result.success = cmd_result.was_successful
		if result.success:
			result.changes = 'User {} added'.format(name)
		result.comment = cmd_result.text

		return result

	def absent(self, name):
		result = StateResult()
		if not self._user_exists(name):
			result.success = True
			result.comment = 'User {} already absent'.format(name)
			return result

		cmd_result = self.session.run_command(['deluser', name])
		result.success = cmd_result.was_successful
		if result.success:
			result.changes = 'User {} deleted'.format(name)
		result.comment = cmd_result.text

	def _user_exists(self, name):
		return self.session.run_command('getent passwd {}'.format(name)).was_successful


def absent(session, args):
	return UserState(session).absent(**args)


def present(session, args):
	return UserState(session).present(**args)
