from unittest import mock
import prove.environment
import prove.states
from prove.locator import _get_file_name, Locator, Component


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
	assert isinstance(states['test_state'], prove.states.StateFile)
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


def test_locate_files():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	with mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_files.return_value = ['/root/files/test_file']
		files = locator.locate_files()
		mock_list_files.assert_called_once_with('/root/files')
	assert 'test_file' in files
	assert '/root/files/test_file' == files['test_file']


def test_locate_components():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	with mock.patch('prove.util.list_subdirs') as mock_list_subdirs:
		mock_list_subdirs.return_value = ['test_component']
		components = locator.locate_components()
		mock_list_subdirs.assert_called_once_with('/root/components')
	assert 'test_component' in components
	assert isinstance(components['test_component'], Component)
	assert 'test_component' == components['test_component'].name


def test_locate_components_with_roles():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	loader.load.return_value = {'states': ['test_state']}
	with mock.patch('prove.util.list_subdirs') as mock_list_subdirs, \
	     mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_subdirs.return_value = ['test_component']
		mock_list_files.side_effect = [['test_role'], [], [], []]
		components = locator.locate_components()
		mock_list_subdirs.assert_called_once_with('/root/components')
	assert 'test_component/test_role' in components['test_component'].roles
	role = components['test_component'].roles['test_component/test_role']
	assert 'test_state' in role.states


def test_locate_components_with_states():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	loader.load.return_value = {'test_state': {}}
	with mock.patch('prove.util.list_subdirs') as mock_list_subdirs, \
	     mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_subdirs.return_value = ['test_component']
		mock_list_files.side_effect = [[], ['test_state'], [], []]
		components = locator.locate_components()
		mock_list_subdirs.assert_called_once_with('/root/components')
	assert 'test_component/test_state' in components['test_component'].state_files
	state_file = components['test_component'].state_files['test_component/test_state']
	loaded_state_file = state_file.load()
	assert 'test_state' == loaded_state_file.states[0].name


def test_locate_components_with_variables():
	loader = mock_loader()
	locator = Locator('/root', [loader])
	loader.load.return_value = {'test_var': {}}
	with mock.patch('prove.util.list_subdirs') as mock_list_subdirs, \
	     mock.patch('prove.util.list_files') as mock_list_files:
		mock_list_subdirs.return_value = ['test_component']
		mock_list_files.side_effect = [[], [], ['test_var_file'], []]
		components = locator.locate_components()
		mock_list_subdirs.assert_called_once_with('/root/components')
	assert 'test_component/test_var_file' in components['test_component'].variable_files
	var_file = components['test_component'].variable_files['test_component/test_var_file']
	assert 'test_var' in var_file.variables
