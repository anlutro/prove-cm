import difflib

from prove.state_functions import AbstractState
from prove.catalog.states import StateFuncResult


class FileState(AbstractState):
	def write_tmpfile(self, source=None, content=None):
		result = self.session.run_command('mktemp --suffix=.prove', skip_sudo=True)
		tmp_path = result.stdout.strip()
		if content:
			self.session.write_to_file(content, tmp_path)
		elif source:
			self.session.upload_file(source, tmp_path)
		return tmp_path

	def upload_tmpdir(self, source):
		raise NotImplementedError()

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

	def stat(self, path, fmt):
		result = self.session.run_command("stat -c '%s' %s" % (fmt, path))
		return result.stdout.strip()

	def ensure_user(self, path, user):
		current_user = self.stat(path, '%U')
		if current_user != user and not self.session.is_dry_run:
			self.session.run_command('chown %s %s' % (user, path))
		return current_user, user

	def ensure_group(self, path, group):
		current_group = self.stat(path, '%G')
		if current_group != group and not self.session.is_dry_run:
			self.session.run_command('chgrp %s %s' % (group, path))
		return current_group, group

	def ensure_mode(self, path, mode):
		current_mode = self.stat(path, '%a')
		if current_mode != mode and not self.session.is_dry_run:
			self.session.run_command('chmod %s %s' % (mode, path))
		return current_mode, mode


class ManagedState(FileState):
	def run(self, path, source=None, content=None, user=None, group=None, mode=None):
		result = StateFuncResult()
		result.changes = []

		file_exists = self.session.run_command('test -f %s' % path).exit_code == 0

		tmpfile = None
		if source or content:
			tmpfile = self.write_tmpfile(source=source, content=content)

		if tmpfile:
			should_move_file = False
			if file_exists:
				diff = self.get_diff(path, tmpfile)
				if diff:
					result.changes.extend(diff)
					should_move_file = True
			else:
				should_move_file = True
				result.changes.append('created file %r' % path)
			if should_move_file and not self.session.is_dry_run:
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
				result.changes.append('mode changed from {} to {}'.format(old_mode, new_mode))

		if not result.changes:
			result.comment = 'no changes to file %r' % path
		result.success = True
		return result


class DirectoryState(FileState):
	def run(self, path, user=None, group=None, mode=None):
		result = StateFuncResult()
		result.changes = []

		dir_exists = self.session.run_command('test -d "%s"' % path).was_successful
		if not dir_exists:
			if not self.session.is_dry_run:
				self.session.run_command('mkdir -p "%s"' % path)
			result.changes.append('created directory %r' % path)

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

		if not result.changes:
			result.comment = 'no changes to directory %r' % path
		result.success = True
		return result


class AbsentState(FileState):
	def run(self, path):
		result = StateFuncResult(success=True)
		exists = self.session.run_command('test -e "%s"' % path).was_successful
		if not exists:
			result.comment = 'file already absent: %r' % path
			return result

		if not self.session.is_dry_run:
			rm_result = self.session.run_command('rm -rfv "%s"' % path)
			result.merge_with_cmd_result(rm_result)
		return result


def managed(session, args):
	return ManagedState(session).run(**args)


def directory(session, args):
	return DirectoryState(session).run(**args)


def absent(session, args):
	return AbsentState(session).run(**args)
