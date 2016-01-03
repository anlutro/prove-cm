from contextlib import contextmanager
import logging
import shlex

import prove.config
import prove.environment

log = logging.getLogger(__name__)


class Connection:
	def __init__(self, host, env):
		assert isinstance(host, prove.config.HostConfig)
		self.host = host
		assert isinstance(env, prove.environment.HostEnvironment)
		self.env = env
		self.info = ConnectionInfo(self)

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


class ConnectionInfo:
	def __init__(self, connection):
		self.connection = connection
		self._lsb_release = None

	def _load_lsb_release(self):
		log.info('Loading lsb_release data')
		result = self.connection.run_command('lsb_release -a -s')
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


class Executor:
	connection_cls = Connection

	def __init__(self, app):
		self.app = app

	@contextmanager
	def connect(self, host):
		log.info('Connecting to host: %s', host.host)
		self.app.output.connect_start(host)
		connection = self.get_connection(host)

		try:
			connection.connect()
			self.app.output.connect_success(host)
		except:
			self.app.output.connect_failure(host)
			raise

		try:
			yield connection
		finally:
			log.info('Diconnecting host: %s', host.host)
			connection.disconnect()
			self.app.output.disconnected(host)

	def get_connection(self, host):
		env = self.app.get_host_env(host)
		return self.connection_cls(host, env)
