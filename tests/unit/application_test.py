import prove.actions
import prove.config
import prove.environment
from prove.application import Application
from unittest import mock


def make_app(options=None, hosts=None):
	if options is None:
		options = {}
	if 'root_dir' not in options:
		options['root_dir'] = '/'
	options = prove.config.Options(options)

	if hosts is None:
		hosts = [{'host': 'localhost'}]
	hosts = [prove.config.HostConfig(**host) for host in hosts]

	env = mock.Mock(spec=prove.environment.Environment)

	return Application(options=options, env=env, hosts=hosts, output=None)


def test_calls_run_on_action_class():
	app = make_app()
	mock_command = mock.Mock(spec=prove.actions.Command)
	app.run_command(mock_command)
	mock_command.run.assert_called_once()
