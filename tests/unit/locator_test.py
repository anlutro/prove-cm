import prove.environment
import prove.state
from prove.locator import _get_file_name, Locator
from unittest import mock


def mock_loader():
	loader = mock.Mock()
	loader.supports = mock.Mock(return_value=True)
	loader.load = mock.Mock()
	return loader


def test_file_name_strips_extension_and_root_dir():
	assert 'foo/bar' == _get_file_name('/states/foo/bar.xyz', '/states')
	assert 'foo/bar' == _get_file_name('/states/foo/bar.abc.xyz', '/states')


def test_locate_roles():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	loader.load.return_value = {'test_role': {}}
	with mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_files.return_value = ['test_role']
		roles = locator.locate_roles()
		mock_list_files.assert_called_once_with('/root/roles')
	assert 'test_role' in roles
	assert isinstance(roles['test_role'], prove.environment.Role)
	assert 'test_role' == roles['test_role'].name


def test_locate_states():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	loader.load.return_value = {'test_state': {}}
	with mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_files.return_value = ['test_state']
		states = locator.locate_states()
		mock_list_files.assert_called_once_with('/root/states')
	assert 'test_state' in states
	assert isinstance(states['test_state'], prove.state.StateFile)
	assert 'test_state' == states['test_state'].name


def test_locate_variables():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	loader.load.return_value = {'test_var': {}}
	with mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_files.return_value = ['test_var']
		variables = locator.locate_variables()
		mock_list_files.assert_called_once_with('/root/variables')
	assert 'test_var' in variables
	assert isinstance(variables['test_var'], prove.environment.VariableFile)
	assert 'test_var' == variables['test_var'].name
