import logging

import prove.operations
from prove.catalog.states import State, StateFuncCall
from prove.catalog.states.runner import SingleStateRunner

LOG = logging.getLogger(__name__)


class StateAction(prove.operations.Action):
	name = 'state'

	def run(self):
		runner = SingleStateRunner(self.session)
		fncall = StateFuncCall(self.args[0], self.kwargs)
		state = State('Ad-hoc single state', [fncall])
		runner.run(state)
