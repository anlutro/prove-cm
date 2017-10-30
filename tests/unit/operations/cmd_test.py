from tests.unit.operations import make_app_conn

from prove.operations.commands.cmd import CmdCommand
from prove.operations.actions.cmd import CmdAction


def test_CmdCommand():
	app, conn = make_app_conn()
	command = CmdCommand(app, args=['test-cmd'])
	command.run()
	action = conn.run_action.call_args[0][0]
	assert isinstance(action, CmdAction)
