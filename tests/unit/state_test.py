import pytest
from prove import state


def test_state_requires_accumulates_invocation_requires():
	s = state.State('s1', [
		state.StateInvocation('f1', {'requires': ['s2']}),
		state.StateInvocation('f2', {'requires': ['s3']}),
	])
	assert ['s2', 's3'] == s.requires


def test_required_states_are_first():
	states = [
		state.State('s1', [
			state.StateInvocation('f1', {'requires': ['s2']})
		]),
		state.State('s2', [
			state.StateInvocation('f2', {})
		])
	]
	sf = state.LoadedStateFile('sf', states)
	states = state.sort_states([sf])
	assert 's2' == states[0].name
	assert 's1' == states[1].name


def test_recursive_require_throws_exception():
	states = [
		state.State('s1', [
			state.StateInvocation('f1', {'requires': ['s2']})
		]),
		state.State('s2', [
			state.StateInvocation('f2', {'requires': ['s1']})
		])
	]
	sf = state.LoadedStateFile('sf', states)
	with pytest.raises(state.StateRequireRecursionException):
		state.sort_states([sf])
