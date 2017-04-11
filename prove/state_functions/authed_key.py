import os.path
from prove.states import StateResult
from prove.state_functions import AbstractState


class AuthedKeyState(AbstractState):
	def parse_key(self, key_str):
		if not key_str or key_str.startswith('#'):
			return None
		parts = key_str.split()
		if len(parts) < 2:
			raise ValueError('invalid key: %r' % key_str)
		enc, key, comment = parts[0], parts[1], None
		if len(parts) > 2:
			comment = parts[2]
		return enc, key, comment

	def parse_authed_keys_file(self, path):
		file_contents = self.session.download_file(path)
		keys = []
		for line in file_contents.splitlines():
			key = self.parse_key(line.strip())
			if key:
				keys.append(key)
		return keys

	def key_exists(self, authed_keys_path, enc, key):
		for ex_enc, ex_key, ex_comment in self.parse_authed_keys_file(authed_keys_path):
			if enc == ex_enc and key == ex_key:
				return True
		return False

	def ensure_present(self, key, user):
		result = StateResult(success=True)

		getent = self.run_command(['getent', 'passwd', user])
		if not getent.was_successful:
			result.merge_with_cmd_result(getent)
			return result

		home_dir = getent.stdout.split(':')[5]
		authed_keys_path = os.path.join(home_dir, '.ssh', 'authorized_keys')

		enc, key, comment = self.parse_key(key)
		if self.key_exists(authed_keys_path, enc, key):
			result.comment = 'key already exists'
			return result

		key_str = '%s %s' % (enc, key)
		key_str_short = '%s %s' % (enc, key[:8] + '...')
		if comment:
			key_str += ' %s' % comment
			key_str_short += ' %s' % comment
		self.run_command('echo "%s" >> %s' % (key_str, authed_keys_path))
		result.changes = 'added public key %r' % key_str_short

		return result

	def ensure_absent(self, key, user):
		result = StateResult(success=True)

		getent = self.run_command(['getent', 'passwd', user])
		if not getent.was_successful:
			result.merge_with_cmd_result(getent)
			return result

		home_dir = getent.stdout.split(':')[5]
		authed_keys_path = os.path.join(home_dir, '.ssh', 'authorized_keys')

		enc, key, comment = self.parse_key(key)
		if not self.key_exists(authed_keys_path, enc, key):
			result.comment = 'key is already absent'
			return result

		key_str = '%s %s' % (enc, key)
		key_str_short = '%s %s' % (enc, key[:8] + '...')
		self.run_command('sed -r -i.bak "/^%s(\s+.*)?$/d" %s' % (key_str, authed_keys_path))
		result.changes = 'removed public key %r' % key_str_short

		return result


def present(session, args):
	return AuthedKeyState(session).ensure_present(**args)


def absent(session, args):
	return AuthedKeyState(session).ensure_absent(**args)
