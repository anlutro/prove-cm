from unittest import mock

import prove.cli.agent_daemon


def test_starts_agent_daemon():
	client = prove.cli.agent_daemon.AgentDaemon(['-b', '1.2.3.4', '-p', '1234'])
	with mock.patch('prove.cli._locate_config') as mock_locate, \
	     mock.patch('prove.cli._read_config') as mock_read, \
	     mock.patch('prove.remote.run_server') as mock_server:
		mock_locate.return_value = '/tmp/prove/prove.yml'
		mock_read.return_value = {'foo': 'bar'}
		client.main()
	mock_server.assert_called_with({
		'options': {
			'root_dir': '/tmp/prove',
			'agent': {
				'bind': '1.2.3.4',
				'port': 1234,
			},
		},
		'foo': 'bar',
	})

