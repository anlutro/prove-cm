from unittest import mock

from tests.unit.actions import make_app_conn

import prove.actions.states
from prove.state import State, StateInvocation, StateResult


def test_StatesAction():
	action = prove.actions.states.StatesAction(args=[])
	state = State('test', [
		StateInvocation('test.noop', {})
	])
	app, conn = make_app_conn([state])
	result = StateResult()
	with mock.patch(
			'prove.states.test.noop',
			new_callable=mock.MagicMock,
			return_value=result,
	) as mock_noop:
		mock_noop.__name__ = 'noop'
		action.run(app=app)
	app.executor_connect.assert_called_once_with('host1')
	app.output.state_invocation_start.assert_called_once_with(
		state, state.invocations[0])
	mock_noop.assert_called_once()
	app.output.state_invocation_finish.assert_called_once_with(
		state, state.invocations[0], result)
