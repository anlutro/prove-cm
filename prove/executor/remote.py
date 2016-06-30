import logging

import prove.executor
import prove.remote.client

LOG = logging.getLogger(__name__)


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

	def run_command(self, *args, **kwargs):
		raise RuntimeError('Remote session does not run commands')

	def _upload_file(self, *args, **kwargs):
		raise RuntimeError('Remote session does not upload files')


class Executor(prove.executor.Executor):
	def get_session(self, target):
		# TODO: remove dummy callback
		def callback(response):
			if not response:
				return
			# print(repr(response))
			if response['data'] and 'output' in response['data']:
				func = getattr(self.app.output, response['data']['output'])
				args = prove.remote.unserialize(response['data']['args'])
				kwargs = prove.remote.unserialize(response['data']['kwargs'])
				func(*args, **kwargs)
			if response['status'] == 'error':
				self.app.output.error(response['data'])

		env = self.get_env(target)
		socket = prove.remote.client.RemoteSocket(
			target.host,
			target.options.get('port', prove.remote.DEFAULT_PORT)
		)
		client = prove.remote.client.RemoteClient(socket, callback, target, env)
		return Session(client, target, env, self.app.output)
