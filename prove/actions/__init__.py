import logging

LOG = logging.getLogger(__name__)


class Action:
	def __init__(self, args):
		self.args = args

	def run(self, session):
		raise NotImplementedError()


class Command:
	action_cls = None # needs to be overridden

	def __init__(self, args):
		self.args = args

	def run(self, app, hosts):
		for host in hosts:
			with app.executor_connect(host) as session:
				self.run_action(session)

	def run_action(self, session):
		action = self.action_cls(self.args)  # pylint: disable=not-callable
		return session.run_action(action)
