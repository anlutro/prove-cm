from unittest import mock
import prove.actions
import prove.client.console


def test_instantiates_correct_action_class():
	with mock.patch('prove.actions.states.StatesCommand', return_value='test_retval'):
		command = prove.client.console.ConsoleClient(['states']).get_command()
		assert 'test_retval' is command


def test_loads_config_file():
	client = prove.client.console.ConsoleClient(['states', '-c', '/dir/test.yml'])
	client.parse_configfile = mock.Mock(return_value={'foo': 'bar'})
	config = client.get_config()
	assert config['foo'] == 'bar'
	client.parse_configfile.assert_called_once_with('/dir/test.yml')


def test_searches_for_config_file_if_not_specified():
	client = prove.client.console.ConsoleClient(['states'])
	client.parse_configfile = mock.Mock(return_value={'foo': 'bar'})
	with mock.patch('prove.client._locate_config') as mock_locate:
		mock_locate.return_value = 'located.yml'
		config = client.get_config()
	assert config['foo'] == 'bar'
	client.parse_configfile.assert_called_once_with('located.yml')
