import importlib
import logging

from prove.util import snake_to_camel_case

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


def get_command_cls(name):
	module_name = name.replace('-', '_')
	command_module_name = 'prove.operations.commands.%s' % module_name
	command_module = importlib.import_module(command_module_name)
	command_cls = snake_to_camel_case(name)
	return getattr(command_module, command_cls + 'Command')


def get_action_cls(name):
	module_name = name.replace('-', '_')
	action_module_name = 'prove.operations.actions.%s' % module_name
	action_module = importlib.import_module(action_module_name)
	action_cls = snake_to_camel_case(name)
	return getattr(action_module, action_cls + 'Action')
