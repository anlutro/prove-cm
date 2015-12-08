import prove.runner
import prove.states.file
import prove.output.null
import prove.environment
from unittest import mock


def test_normalize_state_data():
	data = {'sid': {'mod.fn': {'arg': 'arg'}}}
	data = prove.runner.normalize_state_data(data)
	assert 1 == len(data)
	state_id, state_fn, state_args = data[0]
	assert 'sid' == state_id
	assert 'mod.fn' == state_fn
	assert 'arg' == state_args['arg']

	data = {'sid': [{'fn': 'mod.fn', 'arg': 'arg'}]}
	data = prove.runner.normalize_state_data(data)
	assert 1 == len(data)
	state_id, state_fn, state_args = data[0]
	assert 'sid' == state_id
	assert 'mod.fn' == state_fn
	assert 'arg' == state_args['arg']


def test_get_state_cls():
	state_fn = prove.runner.get_state_cls('file.managed')
	assert prove.states.file.Managed is state_fn


def test_HostRunner_run():
	env = mock.Mock()
	env.get_states = mock.Mock(return_value={})
	ssh_client = mock.Mock()
	options = {'host': 'localhost'}
	output = mock.Mock()

	runner = prove.runner.HostRunner(env, ssh_client, options, output)
	runner.run()
	assert 1 == ssh_client.connect.call_count

def test_HostRunner_run_with_states():
	env = mock.Mock()
	env.get_states = mock.Mock(return_value={})
	ssh_client = mock.Mock()
	options = {'host': 'localhost'}
	output = mock.Mock()

	runner = prove.runner.HostRunner(env, ssh_client, options, output)
	runner.run()
	assert 1 == ssh_client.connect.call_count
