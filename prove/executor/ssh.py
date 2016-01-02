import paramiko
import paramiko.ssh_exception

import prove.executor


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


class Connection(prove.executor.Connection):
	def __init__(self, ssh_client, *args):
		self.ssh_client = ssh_client
		super().__init__(*args)

	def connect(self):
		options = self.host.options
		kwargs = {}
		if options.get('port'):
			kwargs['port'] = options['port']
		if options.get('username'):
			kwargs['username'] = options['username']
		if options.get('password'):
			kwargs['password'] = options['password']
		if options.get('ssh_key'):
			kwargs['key_filename'] = options('ssh_key')
			kwargs['look_for_keys'] = True

		self.ssh_client.connect(self.host.host, **kwargs)

	def disconnect(self):
		self.ssh_client.close()

	def run_command(self, command, timeout=None, get_pty=False):
		if isinstance(command, list):
			command = ' '.join(command)
		chan = self.ssh_client.get_transport().open_session()
		if get_pty:
			chan.get_pty()
		chan.settimeout(timeout)
		chan.exec_command(command)
		return LazyParamikoCommandResult(chan)


class Executor(prove.executor.Executor):
	def get_connection(self, host):
		env = self.app.get_host_env(host)
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		return Connection(ssh_client, host, env)