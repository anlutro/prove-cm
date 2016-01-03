from unittest import mock

from tests.unit.actions import make_app_conn

import prove.executor
import prove.actions.cmd


def test_CmdAction():
	action = prove.actions.cmd.CmdAction(args=['test-cmd'])
	app, conn = make_app_conn()
	result = prove.executor.CommandResult(exit_code=0, stdout='', stderr='')
	conn.run_command = mock.Mock(return_value=result)
	action.run(app=app)
	conn.run_command.assert_called_with(['test-cmd'])
