from unittest import mock

from tests.unit.operations import make_app_conn

from prove.operations.actions.states import StatesAction
from prove.operations.commands.states import StatesCommand
from prove.catalog.states import State, StateFuncCall, StateFuncResult


def test_StatesCommand():
	state = State('test', [
		StateFuncCall('test.noop', {})
	])
	app, conn = make_app_conn([state])
	command = StatesCommand(app, args=[])
	result = StateFuncResult()
	with mock.patch(
			'prove.state_functions.test.noop',
			new_callable=mock.MagicMock,
			return_value=result,
	) as mock_noop:
		mock_noop.__name__ = 'noop'
		command.run()

	app.executor_connect.assert_called_once_with('host1')
	action = conn.run_action.call_args[0][0]
	assert isinstance(action, StatesAction)
