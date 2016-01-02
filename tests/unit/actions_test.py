from unittest import mock
import prove.actions
import prove.executor


def make_app_conn(states=None):
	app = mock.Mock()
	app.hosts = ['host1']
	app.options = {'run_until_no_changes': False}
	context_manager = mock.MagicMock()
	app.executor_connect = mock.Mock(return_value=context_manager)
	conn = context_manager.__enter__()
	conn.env = mock.Mock()
	conn.env.states = states
	return app, conn


def test_StatesAction():
	action = prove.actions.StatesAction(args=[])
	app, _ = make_app_conn([])
	action.run(app=app)
	# TODO: assertions!


def test_CmdAction():
	action = prove.actions.CmdAction(args=['test-cmd'])
	app, conn = make_app_conn()
	result = prove.executor.CommandResult(exit_code=0, stdout='', stderr='')
	conn.run_command = mock.Mock(return_value=result)
	action.run(app=app)
	conn.run_command.assert_called_with(['test-cmd'])
