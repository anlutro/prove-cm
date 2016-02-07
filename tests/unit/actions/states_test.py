from unittest import mock

from tests.unit.actions import make_app_conn

import prove.actions.states
from prove.state import State, StateInvocation, StateResult


def test_StatesCommand():
	command = prove.actions.states.StatesCommand(args=[])
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
		command.run(app=app)

	app.executor_connect.assert_called_once_with('host1')
	action = conn.run_action.call_args[0][0]
	assert isinstance(action, prove.actions.states.StatesAction)
