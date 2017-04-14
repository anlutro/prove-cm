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

	def __call__(self, func, *args, *kwargs):
		self._send(func, args, kwargs)
