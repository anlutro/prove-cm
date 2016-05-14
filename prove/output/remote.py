import prove.remote


class RemoteOutput:
	def __init__(self, send_func):
		self._send_func = send_func

	def _send(self, func, args, kwargs):
		self._send_func('running', {
			'output': func,
			'args': prove.remote.serialize(args),
			'kwargs': prove.remote.serialize(kwargs),
		})

	def connect_start(self, *args, **kwargs):
		self._send('connect_start', args, kwargs)

	def connect_success(self, *args, **kwargs):
		self._send('connect_success', args, kwargs)

	def connect_failure(self, *args, **kwargs):
		self._send('connect_failure', args, kwargs)

	def disconnected(self, *args, **kwargs):
		self._send('disconnected', args, kwargs)

	def cmd_result(self, *args, **kwargs):
		self._send('cmd_result', args, kwargs)

	def state_invocation_start(self, *args, **kwargs):
		self._send('state_invocation_start', args, kwargs)

	def state_invocation_finish(self, *args, **kwargs):
		self._send('state_invocation_finish', args, kwargs)

	def state_summary(self, *args, **kwargs):
		self._send('state_summary', args, kwargs)
