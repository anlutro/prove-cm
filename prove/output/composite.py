class CompositeOutput:
	def __init__(self, *outputters):
		self.outputters = outputters

	def _forward(self, func, args, kwargs):
		for outputter in self.outputters:
			getattr(outputter, func)(*args, **kwargs)

	def __call__(self, func, *args, *kwargs):
		self._forward(func, args, kwargs)
