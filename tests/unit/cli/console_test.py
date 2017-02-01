from unittest import mock
import prove.actions
from prove.cli.action_runner import ActionRunner


def test_instantiates_correct_action_class():
	with mock.patch('prove.actions.states.StatesCommand', return_value='test_retval'):
		command = ActionRunner(['states']).get_command(None)
		assert 'test_retval' == command


def test_loads_config_file():
	client = ActionRunner(['states', '-c', '/dir/test.yml'])
	with mock.patch('prove.cli._read_config') as mock_read:
		mock_read.return_value = {'foo': 'bar'}
		config = client.get_config()
	assert config['foo'] == 'bar'
	mock_read.assert_called_once_with('/dir/test.yml')


def test_searches_for_config_file_if_not_specified():
	client = ActionRunner(['states'])
	with mock.patch('prove.cli._locate_config') as mock_locate, \
	     mock.patch('prove.cli._read_config') as mock_read:
		mock_locate.return_value = 'located.yml'
		mock_read.return_value = {'foo': 'bar'}
		config = client.get_config()
	assert config['foo'] == 'bar'
	mock_read.assert_called_once_with('located.yml')
