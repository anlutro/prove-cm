import logging

LOG = logging.getLogger(__name__)


class Action:
	def __init__(self, session, args, kwargs):
		self.session = session
		self.args = args
		self.kwargs = kwargs

	def run(self):
		raise NotImplementedError()


class Command:
	def __init__(self, app, args=None, kwargs=None):
		self.app = app
		self.args = args or []
		self.args.extend(self._extra_args())
		self.kwargs = kwargs or {}
		self.kwargs.update(self._extra_kwargs())

	def _extra_args(self):
		return []

	def _extra_kwargs(self):
		return {}

	def run(self, targets=None):
		if targets is None:
			targets = self.app.targets

		for target in targets:
			self.run_target(target)

	def run_target(self, target):
		with self.app.executor_connect(target) as session:
			self.run_action(session)

	def run_action(self, session):
		action_cls = getattr(self, 'action_cls')
		if not action_cls:
			raise RuntimeError(('action_cls must be set '
				'or one of the run methods must be overridden'))
		action = action_cls(session, self.args, self.kwargs)
		return session.run_action(action)
