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
		state = prove.states.State('Ad-hoc state', [fncall])
		state_func = runner.get_state_function(fncall.func)
		self.session.output.state_fncall_start(state, fncall)
		result = state_func(self.session, self.kwargs)
		self.session.output.state_fncall_finish(state, fncall, result)


class StateCommand(prove.actions.Command):
	action_cls = StateAction
