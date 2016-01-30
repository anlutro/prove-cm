import logging
import paramiko
import paramiko.ssh_exception

import prove.executor

log = logging.getLogger(__name__)


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
			kwargs['key_filename'] = self.options('ssh_key')
			kwargs['look_for_keys'] = True

		self.ssh_client.connect(self.host.host, **kwargs)

		if self.options.get('sudo'):
			log.debug('Switching to root')
			self.run_command('sudo -su')

	def disconnect(self):
		self.ssh_client.close()

	def run_command(self, command, timeout=None, get_pty=False):
		command = self._cmd_as_string(command)
		log.debug('Running command: `%s`', command)

		chan = self.ssh_client.get_transport().open_session()
		if get_pty:
			chan.get_pty()
		chan.settimeout(timeout)
		chan.exec_command(command)
		return LazyParamikoCommandResult(chan)

	def upload_file(self, local_path, remote_path):
		if local_path.startswith('http://') or local_path.startswith('https://'):
			if self.run_command('which wget').was_successful:
				return self.run_command('wget -nv {} -O {}'.format(local_path, remote_path)).was_successful
			elif self.run_command('which curl').was_successful:
				return self.run_command('curl {} -o {}'.format(local_path, remote_path)).was_successful
			raise Exception('curl or wget not found')

		if local_path.startswith('prove://'):
			local_path = self._locate_file(local_path)

		sftp = paramiko.SFTPClient.from_transport(self.ssh_client.get_transport())
		sftp.put(local_path, remote_path)
		sftp.close()
		return True

	def _locate_file(self):
		raise NotImplementedError()


class Executor(prove.executor.Executor):
	def get_session(self, host):
		env = self.app.get_host_env(host)
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		return Session(ssh_client, host, env)
