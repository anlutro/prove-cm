import prove.state.runner
import prove.states.file
import prove.output.null
import prove.environment
from unittest import mock


def make_runner(states=None, options=None):
	if states is None:
		states = {}
	if options is None:
		options = {'host': 'localhost'}
	env = mock.Mock()
	env.get_states = mock.Mock(return_value=states)
	ssh_client = mock.Mock()
	output = mock.Mock()

	return prove.state.runner.HostRunner(env, ssh_client, options, output)


def test_normalize_state_data():
	data = {'sid': {'mod.fn': {'arg': 'arg'}}}
	data = prove.state.runner.normalize_state_data(data)
	assert 1 == len(data)
	state_id, state_fn, state_args = data[0]
	assert 'sid' == state_id
	assert 'mod.fn' == state_fn
	assert 'arg' == state_args['arg']

	data = {'sid': [{'fn': 'mod.fn', 'arg': 'arg'}]}
	data = prove.state.runner.normalize_state_data(data)
	assert 1 == len(data)
	state_id, state_fn, state_args = data[0]
	assert 'sid' == state_id
	assert 'mod.fn' == state_fn
	assert 'arg' == state_args['arg']


def test_get_state_cls():
	runner = make_runner()
	state_fn = runner.get_state_cls('file.managed')
	assert prove.states.file.Managed is state_fn


def test_HostRunner_run():
	runner = make_runner()
	runner.run()
	assert 1 == runner.ssh_client.connect.call_count


def test_HostRunner_run_with_states():
	runner = make_runner()
	runner.run()
	assert 1 == runner.ssh_client.connect.call_count
