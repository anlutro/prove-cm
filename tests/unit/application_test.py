import prove.actions
import prove.config
import prove.environment
from prove.application import Application
from unittest import mock


def make_app(options=None, targets=None):
	if options is None:
		options = {}
	if 'root_dir' not in options:
		options['root_dir'] = '/'
	options = prove.config.Options(options)

	if targets is None:
		targets = [{'host': 'localhost'}]
	targets = [prove.config.Target(**target) for target in targets]

	env = mock.Mock(spec=prove.environment.Environment)

	return Application(options=options, env=env, targets=targets, output=None)


def test_calls_run_on_action_class():
	app = make_app()
	mock_command = mock.Mock(spec=prove.actions.Command)
	app.run_command(mock_command)
	mock_command.run.assert_called_once()
