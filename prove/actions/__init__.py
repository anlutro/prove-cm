class Action:
	def __init__(self, args):
		self.args = args

	def run(self, session):
		raise NotImplementedError()


class Command:
	action_cls = None # needs to be overridden

	def __init__(self, args):
		self.args = args

	def run(self, app):
		for host in app.hosts:
			with app.executor_connect(host) as session:
				self.run_action(session)

	def run_action(self, session):
		action = self.action_cls(self.args)  # pylint: disable=not-callable
		return session.run_action(action)
