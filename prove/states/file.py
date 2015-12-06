import tempfile

from prove.states import State

__hidden__ = ['FileState']


class FileState(State):
	def _ensure_ownership(self, path, user=None, group=None):
		if user is None and group is None:
			return

		if user and group:
			chown_arg = '{}:{}'.format(user, group)
		elif user:
			chown_arg = user
		elif group:
			chown_arg = ':group'
		return self._run_command('chown -c {} {}'.format(chown_arg, path))

	def _ensure_mode(self, path, mode):
		return self._run_command('chmod -c {} {}'.format(mode, path))


class Absent(State):
	def run(self, path=None):
		result = self._run_command('rm -v {}'.format(path))
		if result.was_successful:
			return True, result.stdout
		return False, result.stderr


class Present(FileState):
	def run(self, path=None, user=None, group=None, mode=None):
		changes = []

		result = self._run_command('test -f {}'.format(path))
		if not result.was_successful:
			return False, 'Path is not a file or does not exist'

		if user is not None or group is not None:
			result = self._ensure_ownership(path, user, group)
			if not result.was_successful:
				return False, result.stderr
			if result.stdout:
				changes += result.stdout

		if mode is not None:
			result = self._ensure_mode(path, mode)
			if not result.was_successful:
				return False, result.stderr
			if result.stdout:
				changes += result.stdout

		return True, changes


class Managed(FileState):
	def run(self, path=None, contents=None, source=None, user=None, group=None, mode=None):
		changes = []

		if contents:
			if contents[-1] != '\n':
				contents += '\n'
			file = tempfile.NamedTemporaryFile()
			file.write(contents.encode('utf-8'))
			file.seek(0)
		elif source:
			file = open(source, 'r')

		sftp = self._client.open_sftp()
		sftp.putfo(file, path)
		sftp.close()
		file.close()

		if user is not None or group is not None:
			result = self._ensure_ownership(path, user, group)
			if not result.was_successful:
				return False, result.stderr
			if result.stdout:
				changes += result.stdout

		if mode is not None:
			result = self._ensure_mode(path, mode)
			if not result.was_successful:
				return False, result.stderr
			if result.stdout:
				changes += result.stdout

		return True, changes
