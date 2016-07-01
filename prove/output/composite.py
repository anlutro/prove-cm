class CompositeOutput:
	def __init__(self, *outputters):
		self.outputters = outputters

	def _forward(self, func, args, kwargs):
		for outputter in self.outputters:
			getattr(outputter, func)(*args, **kwargs)

	def connect_start(self, *args, **kwargs):
		self._forward('connect_start', args, kwargs)

	def connect_success(self, *args, **kwargs):
		self._forward('connect_success', args, kwargs)

	def connect_failure(self, *args, **kwargs):
		self._forward('connect_failure', args, kwargs)

	def disconnected(self, *args, **kwargs):
		self._forward('disconnected', args, kwargs)

	def cmd_result(self, *args, **kwargs):
		self._forward('cmd_result', args, kwargs)

	def state_invocation_start(self, *args, **kwargs):
		self._forward('state_invocation_start', args, kwargs)

	def state_invocation_finish(self, *args, **kwargs):
		self._forward('state_invocation_finish', args, kwargs)

	def state_summary(self, *args, **kwargs):
		self._forward('state_summary', args, kwargs)

	def comment(self, *args, **kwargs):
		self._forward('comment', args, kwargs)
