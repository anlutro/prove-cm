import difflib

from prove.states import StateResult


class FileState:
	def __init__(self, session):
		self.session = session

	def upload_tmpfile(self, source):
		result = self.session.run_command('mktemp --suffix=.prove', skip_sudo=True)
		tmp_path = result.stdout.strip()
		self.session.upload_file(source, tmp_path)
		return tmp_path

	def upload_tmpdir(self, source):
		result = self.session.run_command('mktemp --suffix=.prove')
		return result.stdout.strip()

	def get_diff(self, path1, path2):
		def get_file_lines(path):
			result = self.session.run_command('cat {}'.format(path))
			return result.stdout.splitlines()

		diff = difflib.unified_diff(get_file_lines(path1), get_file_lines(path2))
		if diff:
			diff = [line.rstrip() for line in diff]
			diff = diff[2:]
		return diff

	def move_tmpfile(self, tmpfile, path):
		return self.session.run_command('mv %s %s' % (tmpfile, path))

	def _stat(self, path, fmt):
		result = self.session.run_command("stat -c '%s' %s" % (fmt, path))
		return result.stdout.strip()

	def ensure_user(self, path, user):
		current_user = self._stat(path, '%U')
		if current_user != user:
			self.session.run_command('chown %s %s' % (user, path))
		return current_user, user

	def ensure_group(self, path, group):
		current_group = self._stat(path, '%G')
		if current_group != group:
			self.session.run_command('chgrp %s %s' % (group, path))
		return current_group, group

	def ensure_mode(self, path, mode):
		current_mode = self._stat(path, '%a')
		if current_mode != mode:
			self.session.run_command('chmod %s %s' % (mode, path))
		return current_mode, mode


class FileManagedState(FileState):
	def run(self, path, source=None, content=None, user=None, group=None, mode=None):
		result = StateResult()
		result.changes = []

		file_exists = self.session.run_command('test -f %s' % path).exit_code == 0

		if source is not None:
			tmpfile = self.upload_tmpfile(source)
			should_move_file = False
			if file_exists:
				diff = self.get_diff(path, tmpfile)
				if diff:
					result.changes.extend(diff)
					should_move_file = True
			else:
				should_move_file = True
				result.changes.append('file created: %s' % path)
			if should_move_file:
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
				result.changes.append('mode changed from {} to {}'.format(old_mode, new_mode))

		result.success = True
		return result


def managed(session, args):
	return FileManagedState(session).run(**args)
