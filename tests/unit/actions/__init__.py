from unittest import mock


def make_app_conn(states=None):
	app = mock.Mock()
	app.targets = ['host1']
	app.options = {'run_until_no_changes': False}
	context_manager = mock.MagicMock()
	app.executor_connect = mock.Mock(return_value=context_manager)
	conn = context_manager.__enter__()
	conn.env = mock.Mock()
	conn.env.states = states
	return app, conn
