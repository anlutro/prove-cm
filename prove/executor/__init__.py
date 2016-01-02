from contextlib import contextmanager
import logging

import prove.config
import prove.environment

log = logging.getLogger(__name__)


class Connection:
	def __init__(self, host, env):
		assert isinstance(host, prove.config.HostConfig)
		self.host = host
		assert isinstance(env, prove.environment.HostEnvironment)
		self.env = env

	def connect(self):
		raise NotImplementedError()

	def disconnect(self):
		raise NotImplementedError()

	def run_command(self):
		raise NotImplementedError()


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
