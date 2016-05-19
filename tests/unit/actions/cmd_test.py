from unittest import mock

from tests.unit.actions import make_app_conn

import prove.executor
import prove.actions.cmd


def test_CmdCommand():
	app, conn = make_app_conn()
	command = prove.actions.cmd.CmdCommand(app, args=['test-cmd'])
	command.run()
	action = conn.run_action.call_args[0][0]
	assert isinstance(action, prove.actions.cmd.CmdAction)
