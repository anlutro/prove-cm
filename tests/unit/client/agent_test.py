from unittest import mock

import prove.client.agent


def test_starts_agent_daemon():
	client = prove.client.agent.AgentDaemon(['-b', '1.2.3.4', '-p', '1234'])
	with mock.patch('prove.client._locate_config') as mock_locate, \
	     mock.patch('prove.client._read_config') as mock_read, \
	     mock.patch('prove.remote.server.run_server') as mock_server:
		mock_read = mock.Mock(return_value={'foo': 'bar'})
		client.main()
	mock_server.assert_called_with('1.2.3.4', '1234')

