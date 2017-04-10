import logging

import prove.executor
import prove.remote

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

	def upload_file(self, *args, **kwargs):
		raise RuntimeError('Remote session does not upload files')

	def write_to_file(self, *args, **kwargs):
		raise RuntimeError('Remote session does not write to files')


class Executor(prove.executor.Executor):
	def get_session(self, target):
		def callback(response):
			if not response:
				return
			if response['status'] == 'error':
				self.app.output.remote_error(response['data'], target)
			elif response['data'] and 'output' in response['data']:
				func = getattr(self.app.output, response['data']['output'])
				args = prove.remote.unserialize(response['data']['args'])
				kwargs = prove.remote.unserialize(response['data']['kwargs'])
				func(*args, **kwargs)

		env = self.get_env(target)
		client = prove.remote.get_client(target, env, callback)
		return Session(client, target, env, self.app.output)
