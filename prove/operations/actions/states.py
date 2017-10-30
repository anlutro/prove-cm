import prove.operations
from prove.catalog.states.runner import run_states


class StatesAction(prove.operations.Action):
	name = 'states'

	def run(self):
		parallelism = self.kwargs.get('parallelism', None)
		run_states(self.session, parallelism=parallelism)
