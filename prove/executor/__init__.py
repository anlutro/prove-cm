from contextlib import contextmanager
import logging
import tempfile

from lazy import lazy

import prove.config
import prove.environment
import prove.util

LOG = logging.getLogger(__name__)


class Session:
	def __init__(self, target, env, output):
		assert isinstance(target, prove.config.Target)
		self.target = target
		assert isinstance(env, prove.environment.TargetEnvironment)
		self.env = env
		self.output = output
		self.options = env.options
		self.info = SessionInfo(self)

	def connect(self):
		raise NotImplementedError()

	def disconnect(self):
		raise NotImplementedError()

	def run_action(self, command):
		raise NotImplementedError()

	def run_command(self, command, skip_sudo=False):
		raise NotImplementedError()

	def manage_file(self, remote_path, source=None, content=None):
		if not source and not content:
			raise ValueError('must provide source or content!')

		if content:
			self.write_to_file(content, remote_path)

		if source.startswith('http://') or source.startswith('https://'):
			if self.run_command('which wget').was_successful:
				return self.run_command('wget -nv {} -O {}'.format(source, remote_path)).was_successful
			elif self.run_command('which curl').was_successful:
				return self.run_command('curl {} -o {}'.format(source, remote_path)).was_successful
			raise Exception('curl or wget not found')

		if source.startswith('prove://'):
			source = source.replace('prove://', '')
			source = self.env.files[source]
			return self.upload_file(source, remote_path)

		if source.startswith('file://'):
			return self.run_command('cp {} {}'.format(source, remote_path)).was_successful

		raise Exception('Unknown file protocol: %s', source)

	def upload_file(self, source, remote_path):
		raise NotImplementedError()

	def write_to_file(self, content, remote_path):
		raise NotImplementedError()


class SessionInfo:
	def __init__(self, session):
		self.session = session

	@lazy
	def _lsb_release(self):
		result = self.session.run_command('lsb_release -a')
		ret = {}
		for line in result.stdout.splitlines():
			key, val = line.strip().split(':', 1)
			ret[key.strip()] = val.strip()
		return ret

	@property
	def distro(self):
		return self._lsb_release['Distributor ID']

	@property
	def distro_version(self):
		return self._lsb_release['Release']

	def program_exists(self, program):
		result = self.session.run_command(['which', program])
		return result.stdout.strip() if result.was_successful else False

class CommandResult:
	def __init__(self, exit_code, stdout, stderr):
		self.exit_code = exit_code
		self.stdout = stdout.strip()
		self.stderr = stderr.strip()

	@property
	def was_successful(self):
		return self.exit_code == 0

	@property
	def text(self):
		return '\n'.join([self.stdout, self.stderr])


class Executor:
	session_cls = Session

	def __init__(self, app):
		self.app = app

	@contextmanager
	def connect(self, target):
		session = self.get_session(target)
		LOG.info('Connecting to target: %s', target.host)
		self.app.output.connect_start(target)

		try:
			session.connect()
			self.app.output.connect_success(target)
		except:
			self.app.output.connect_failure(target)
			raise

		try:
			yield session
		finally:
			LOG.info('Diconnecting target: %s', target.host)
			session.disconnect()
			self.app.output.disconnected(target)

	def get_session(self, target):
		env = self.get_env(target)
		return self.session_cls(target, env, self.app.output)

	def get_env(self, target):
		LOG.debug('Creating environment for target: %s', target.host)
		env = self.app.get_target_env(target)
		LOG.debug('Host environment options: %s', env.options)
		LOG.debug('Host environment states: %s', env.states)
		LOG.debug('Host environment variables: %s', env.variables)
		return env
