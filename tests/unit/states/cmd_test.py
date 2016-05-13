from unittest import mock
from prove.states import cmd


def test_run():
	cmd_result = mock.Mock()
	cmd_result.was_successful = True
	cmd_result.stdout = 'stdout'
	cmd_result.stderr = 'stderr'
	conn = mock.Mock()
	conn.run_command = mock.Mock(return_value=cmd_result)

	state_result = cmd.run(conn, {'cmd': 'fake_command'})
	conn.run_command.assert_called_once_with('fake_command')
	assert True == state_result.success
	assert 'STDERR:\nstderr\nSTDOUT:\nstdout' == state_result.comment
