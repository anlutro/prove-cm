import logging

import prove.actions
import prove.states
import prove.states.runner

LOG = logging.getLogger(__name__)


class StateAction(prove.actions.Action):
	name = 'state'

	def run(self):
		runner = prove.states.runner.StateRunner(self.session, states={})
		fncall = prove.states.StateFuncCall(self.args[0], self.kwargs)
		state = prove.states.State('Ad-hoc single state', [fncall])
		runner.run_single(state)


class StateCommand(prove.actions.Command):
	action_cls = StateAction
