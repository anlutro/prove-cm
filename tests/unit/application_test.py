import prove.operations
import prove.config
import prove.catalog
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

	catalog = mock.Mock(spec=prove.catalog.Catalog)

	return Application(options=options, catalog=catalog, targets=targets, output=None)


def test_calls_run_on_action_class():
	app = make_app()
	mock_command = mock.Mock(spec=prove.operations.Command)
	app.run_command(mock_command)
	mock_command.run.assert_called_once_with(app.targets)
