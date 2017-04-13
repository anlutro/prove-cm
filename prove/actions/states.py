import logging

import prove.actions
import prove.states.runner

LOG = logging.getLogger(__name__)


class StatesAction(prove.actions.Action):
	name = 'states'

	def run(self):
		parallelism = self.kwargs.get('parallelism', None)

		if parallelism is None:
			state_run = prove.states.runner.StateRunner(self.session)
		else:
			state_run = prove.states.runner.ParallelizedStateRunner(
				self.session, parallelism=int(parallelism),
			)
		state_run.run()


class StatesCommand(prove.actions.Command):
	action_cls = StatesAction

	def _extra_kwargs(self):
		return {'parallelism': self.app.options.get('state_parallelism')}

	def run(self, targets=None):
		if targets is None:
			targets = self.app.targets

		if self.app.options.get('run_until_no_changes'):
			self._run_until_no_changes(targets)
		else:
			self._run_once(targets)

	def _run_once(self, targets):
		for target in targets:
			with self.app.executor_connect(target) as session:
				self.run_action(session)

	def _run_until_no_changes(self, targets):
		num_changes = -1
		while num_changes != 0:
			num_changes = 0
			for target in targets:
				with self.app.executor_connect(target) as session:
					result = self.run_action(session)
					if result.num_states_with_changes == 0:
						targets.remove(target)
					num_changes += result.num_states_with_changes
