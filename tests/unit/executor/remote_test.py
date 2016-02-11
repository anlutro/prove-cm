from unittest import mock

import prove.config
import prove.environment
import prove.executor.remote

def _make_session(remote_client, host=None, env=None, output=None):
	return prove.executor.remote.Session(
		remote_client,
		env or prove.config.HostConfig('localhost'),
		host or prove.environment.HostEnvironment({}, [], {}, {}),
		output or mock.Mock(),
	)


def test_session_calls_remote_client():
	remote_client = mock.Mock()
	session = _make_session(remote_client)
	session.connect()
	remote_client.connect.assert_called_once_with()
	session.run_action('asdf')
	remote_client.run_action.assert_called_once_with('asdf')
	session.disconnect()
	remote_client.disconnect.assert_called_once_with()
