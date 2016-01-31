from contextlib import contextmanager
import logging
import shlex

import prove.config
import prove.environment

log = logging.getLogger(__name__)


class Session:
	def __init__(self, host, env):
		assert isinstance(host, prove.config.HostConfig)
		self.host = host
		assert isinstance(env, prove.environment.HostEnvironment)
		self.env = env
		self.options = env.options
		self.info = SessionInfo(self)

	def _cmd_as_list(self, command):
		if not isinstance(command, list):
			command = shlex.split(command)
		if len(command) == 1 and ' ' in command[0]:
			command = shlex.split(command[0])
		return command

	def _cmd_as_string(self, command):
		if isinstance(command, list):
			command = ' '.join(command)
		return command

	def connect(self):
		raise NotImplementedError()

	def disconnect(self):
		raise NotImplementedError()

	def run_command(self, command):
		raise NotImplementedError()

	def upload_file(self, source, path):
		if source.startswith('http://') or source.startswith('https://'):
			if self.run_command('which wget').was_successful:
				return self.run_command('wget -nv {} -O {}'.format(source, path)).was_successful
			elif self.run_command('which curl').was_successful:
				return self.run_command('curl {} -o {}'.format(source, path)).was_successful
			raise Exception('curl or wget not found')

		if source.startswith('prove://'):
			source = source.replace('prove://', '')
			source = self.env.files[source]
			return self._upload_file(source, path)

		if source.startswith('file://'):
			return self.run_command('cp {} {}'.format(source, path)).was_successful

		raise Exception('Unknown file protocol: %s', source)

	def _upload_file(self, source, path):
		raise NotImplementedError()


class SessionInfo:
	def __init__(self, session):
		self.session = session
		self._lsb_release = None

	def _load_lsb_release(self):
		log.info('Loading lsb_release data')
		result = self.session.run_command('lsb_release -a -s')
		self._lsb_release = result.stdout.splitlines()

	@property
	def distro(self):
		if self._lsb_release is None:
			self._load_lsb_release()
		return self._lsb_release[0]

	@property
	def distro_version(self):
		if self._lsb_release is None:
			self._load_lsb_release()
		return self._lsb_release[2]


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
	def connect(self, host):
		log.info('Connecting to host: %s', host.host)
		self.app.output.connect_start(host)
		session = self.get_session(host)

		try:
			session.connect()
			self.app.output.connect_success(host)
		except:
			self.app.output.connect_failure(host)
			raise

		try:
			yield session
		finally:
			log.info('Diconnecting host: %s', host.host)
			session.disconnect()
			self.app.output.disconnected(host)

	def get_session(self, host):
		log.debug('Creating host environment for host: %s', host.host)
		env = self.app.get_host_env(host)
		log.debug('Host environment options: %s', env.options)
		log.debug('Host environment states: %s', env.states)
		log.debug('Host environment variables: %s', env.variables)
		return self.session_cls(host, env)
