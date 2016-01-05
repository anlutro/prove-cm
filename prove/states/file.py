from prove.state import StateResult


class _FileState:
	def __init__(self, session):
		self.session = session

	def upload_tmpfile(self, source):
		raise NotImplementedError()

	def get_diff(self, path1, path2):
		raise NotImplementedError()

	def move_tmpfile(self, tmpfile, path):
		raise NotImplementedError()

	def ensure_user(self, path, user):
		raise NotImplementedError()

	def ensure_group(self, path, group):
		raise NotImplementedError()

	def ensure_mode(self, path, mode):
		raise NotImplementedError()


class FileManagedState(_FileState):
	def run(self, path, source=None, user=None, group=None, mode=None):
		result = StateResult()
		result.changes = []

		if source is not None:
			tmpfile = self.upload_tmpfile(source)
			result.changes += self.get_diff(path, tmpfile)
			self.move_tmpfile(tmpfile, path)

		if user is not None:
			old_user, new_user = self.ensure_user(path, user)
			if old_user != new_user:
				result.changes.append('user changed from {} to {}'.format(old_user, new_user))

		if group is not None:
			old_group, new_group = self.ensure_group(path, group)
			if old_group != new_group:
				result.changes.append('group changed from {} to {}'.format(old_group, new_group))

		if mode is not None:
			old_mode, new_mode = self.ensure_mode(path, mode)
			if old_mode != new_mode:
				result.changes.append('Mode changed from {} to {}'.format(old_mode, new_mode))

		return result


def managed(session, args):
	return FileManagedState(session).run(**args)
