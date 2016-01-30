import difflib

from prove.state import StateResult


class _FileState:
	def __init__(self, session):
		self.session = session

	def upload_tmpfile(self, source):
		result = self.session.run_command('mktemp --suffix=.prove')
		tmp_path = result.stdout.strip()
		self.session.upload_file(source, tmp_path)
		return tmp_path

	def upload_tmpdir(self, source):
		result = self.session.run_command('mktemp --suffix=.prove')
		return result.stdout.strip()

	def get_diff(self, path1, path2):
		def get_file_lines(path):
			if self.session.run_command('test -f {}'.format(path)).was_successful:
				result = self.session.run_command('cat {}'.format(path))
				return result.stdout.splitlines()
			else:
				return []

		diff = difflib.unified_diff(get_file_lines(path1), get_file_lines(path2))
		if diff:
			diff = [line.rstrip() for line in diff]
			diff = diff[2:]
		return diff

	def move_tmpfile(self, tmpfile, path):
		return self.session.run_command('mv {} {}'.format(tmpfile, path))

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
			result.changes.extend(self.get_diff(path, tmpfile))
			mv_result = self.move_tmpfile(tmpfile, path)

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

		result.success = True
		return result


def managed(session, args):
	return FileManagedState(session).run(**args)
