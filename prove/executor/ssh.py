import logging
import paramiko
import paramiko.ssh_exception

import prove.executor
import prove.util

LOG = logging.getLogger(__name__)


class LazyParamikoCommandResult(prove.executor.CommandResult):
	def __init__(self, chan, bufsize=-1):
		self._chan = chan
		self.stdin = chan.makefile('wb', bufsize)
		self._stdout = chan.makefile('r', bufsize)
		self._stderr = chan.makefile_stderr('r', bufsize)
		self._exit_code = None

	@property
	def stderr(self):
		if not isinstance(self._stderr, str):
			self._stderr = self._stderr.read().decode()
		return self._stderr

	@property
	def stdout(self):
		if not isinstance(self._stdout, str):
			self._stdout = self._stdout.read().decode()
		return self._stdout

	@property
	def exit_code(self):
		if self._exit_code is None:
			self._exit_code = self._chan.recv_exit_status()
		return self._exit_code


class Session(prove.executor.Session):
	def __init__(self, ssh_client, *args):
		self.ssh_client = ssh_client
		self.sftp_client = None
		super().__init__(*args)

	def connect(self):
		kwargs = {}
		if self.options.get('port'):
			kwargs['port'] = self.options['port']
		if self.options.get('username'):
			kwargs['username'] = self.options['username']
		if self.options.get('password'):
			kwargs['password'] = self.options['password']
		if self.options.get('ssh_key'):
			kwargs['key_filename'] = self.options['ssh_key']
			kwargs['look_for_keys'] = False

		self.ssh_client.connect(self.target.host, **kwargs)
		self.sftp_client = paramiko.SFTPClient.from_transport(
			self.ssh_client.get_transport()
		)

		if self.options.get('sudo'):
			result = self.run_command('sudo -n -v', skip_sudo=True)
			if result.exit_code > 0:
				raise Exception(result.stderr.strip())

	def disconnect(self):
		self.ssh_client.close()
		if self.sftp_client:
			self.sftp_client.close()

	def _run_command(self, command):
		chan = self.ssh_client.get_transport().open_session()
		chan.settimeout(None)
		chan.exec_command(command)
		return LazyParamikoCommandResult(chan)

	def write_to_file(self, content, remote_path):
		with self.sftp_client.open(remote_path, 'w+') as remote_file:
			remote_file.write(content)
		return True

	def upload_file(self, local_path, remote_path):
		self.sftp_client.put(local_path, remote_path)
		return True


class Executor(prove.executor.Executor):
	def get_session(self, target):
		env = self.get_env(target)
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		return Session(ssh_client, target, env, self.app.output)
