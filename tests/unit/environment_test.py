import os.path
import prove.environment
from unittest import mock

TEST_ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

def _get_path(*args):
	return os.path.join(TEST_ROOT_DIR, 'files', 'environment_test', *args)


def _assert_scanned(scanned, scan_type, cls):
	key = 'test_' + scan_type
	assert 1 == len(scanned)
	assert isinstance(scanned[key], cls)
	assert 'test_' + scan_type == scanned[key].name
	expected_path = os.path.join(
		TEST_ROOT_DIR,
		_get_path('{}s/{}.yml'.format(scan_type, key))
	)
	assert expected_path == scanned[key].path

def _test_scan(scan_type, cls):
	scanned = prove.environment._scan(
		TEST_ROOT_DIR,
		_get_path('{}s'.format(scan_type)),
		cls
	)
	_assert_scanned(scanned, scan_type, cls)
	return scanned['test_'+scan_type]

def test_scan_roles():
	_test_scan('role', prove.environment.Role)

def test_scan_variables():
	_test_scan('variable', prove.environment.Variable)

def test_scan_states():
	_test_scan('state', prove.environment.State)


def test_load_role():
	role = prove.environment.Role('test_role', _get_path('roles', 'test_role.yml'))
	fl = prove.environment.FileLoader(TEST_ROOT_DIR, ['yaml_mako', 'yaml', 'json'])
	data = fl.load_role(role)
	assert ['test_variable'] == data['variables']
	assert ['test_state'] == data['states']

def test_load_variable():
	variable = prove.environment.Variable('test_variable', _get_path('variables', 'test_variable.yml'))
	fl = prove.environment.FileLoader(TEST_ROOT_DIR, ['yaml_mako', 'yaml', 'json'])
	data = fl.load_variable(variable, {})
	assert {'foo': 'bar'} == data

def test_load_state():
	state = prove.environment.State('test_state', _get_path('states', 'test_state.yml'))
	fl = prove.environment.FileLoader(TEST_ROOT_DIR, ['yaml_mako', 'yaml', 'json'])
	data = fl.load_state(state, {})
	assert {'test_state': [{'fn': 'something.something', 'arg': 'something'}]} == data


def test_environment():
	env = prove.environment.Environment.from_path(_get_path(), ['yaml_mako', 'yaml', 'json'])
	assert 'test_role' in env.roles
	assert 'test_variable' in env.variables
	assert 'test_state' in env.states


def test_environment_make_host_env():
	env = prove.environment.Environment.from_path(_get_path(), ['yaml_mako', 'yaml', 'json'])

	host_env = env.make_host_env([], [], [])
	assert 0 == len(host_env.variables)
	assert 0 == len(host_env.states)

	host_env = env.make_host_env(['test_role'], [], [])
	assert 'test_variable' in host_env.variables
	assert 'test_state' in host_env.states

	host_env = env.make_host_env([], ['test_variable'], [])
	assert 'test_variable' in host_env.variables
	assert 0 == len(host_env.states)

	host_env = env.make_host_env([], [], ['test_state'])
	assert 0 == len(host_env.variables)
	assert 'test_state' in host_env.states
