class Action:
	def __init__(self, args):
		self.args = args

	def run(self, app):
		raise NotImplementedError()
