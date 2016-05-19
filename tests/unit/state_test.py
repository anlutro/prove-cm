import pytest
from prove import states


def test_state_requires_accumulates_invocation_requires():
	s = states.State('s1', [
		states.StateInvocation('f1', {'requires': ['s2']}),
		states.StateInvocation('f2', {'requires': ['s3']}),
	])
	assert ['s2', 's3'] == s.requires


def test_required_states_are_first():
	s = [
		states.State('s1', [
			states.StateInvocation('f1', {'requires': ['s2']})
		]),
		states.State('s2', [
			states.StateInvocation('f2', {})
		])
	]
	sf = states.LoadedStateFile('sf', s)
	s = states.sort_states([sf])
	assert 's2' == s[0].name
	assert 's1' == s[1].name


def test_recursive_require_throws_exception():
	s = [
		states.State('s1', [
			states.StateInvocation('f1', {'requires': ['s2']})
		]),
		states.State('s2', [
			states.StateInvocation('f2', {'requires': ['s1']})
		])
	]
	sf = states.LoadedStateFile('sf', s)
	with pytest.raises(states.StateRequireRecursionException):
		states.sort_states([sf])
