class CommandResult():
	def __init__(self, chan, bufsize=-1):
		self._chan = chan
		self.stdin = chan.makefile('wb', bufsize)
		self._stdout = chan.makefile('r', bufsize)
		self._stderr = chan.makefile_stderr('r', bufsize)
		self._exit_status = None

	@property
	def stderr(self):
		if not isinstance(self._stderr, list):
			self._stderr = self._stderr.readlines()
		return self._stderr

	@property
	def stdout(self):
		if not isinstance(self._stdout, list):
			self._stdout = self._stdout.readlines()
		return self._stdout

	@property
	def exit_status(self):
		if self._exit_status is None:
			self._exit_status = self._chan.recv_exit_status()
		return self._exit_status

	@property
	def was_successful(self):
		return self.exit_status == 0


class State():
	def __init__(self, client):
		self._client = client

	def _run_command(self, command, bufsize=-1, timeout=None, get_pty=False):
		chan = self._client.get_transport().open_session(timeout=timeout)
		if get_pty:
		    chan.get_pty()
		chan.settimeout(timeout)
		chan.exec_command(command)
		return CommandResult(chan, bufsize)
