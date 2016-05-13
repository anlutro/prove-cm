import logging

import prove.executor
import prove.remote.client

log = logging.getLogger(__name__)


class Session(prove.executor.Session):
	def __init__(self, remote_client, *args):
		self.remote_client = remote_client
		super().__init__(*args)

	def connect(self):
		self.remote_client.connect()

	def disconnect(self):
		self.remote_client.disconnect()

	def run_action(self, action):
		return self.remote_client.run_action(action)

	def run_command(self, command, timeout=None, get_pty=False):
		raise RuntimeError('Remote session does not run commands')

	def _upload_file(self, local_path, remote_path):
		raise RuntimeError('Remote session does not upload files')


class Executor(prove.executor.Executor):
	def get_session(self, host):
		# TODO: remove dummy callback
		def callback(data):
			if data:
				print(repr(data))

		env = self.app.get_host_env(host)
		socket = prove.remote.client.RemoteSocket(
			host.host,
			host.options.get('port', prove.remote.DEFAULT_PORT)
		)
		client = prove.remote.client.RemoteClient(socket, callback, host, env)
		return Session(client, host, env, self.app.output)
