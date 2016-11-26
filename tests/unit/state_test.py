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


def test_lazy_state():
	sf = states.LoadedStateFile('sf', [
		states.State('s1', [
			states.StateInvocation('f1', {'lazy': True})
		]),
	])
	assert [] == states.sort_states([sf])


def test_notify_lazy_state():
	sf = states.LoadedStateFile('sf', [
		states.State('s1', [
			states.StateInvocation('f1', {'lazy': True})
		]),
		states.State('s2', [
			states.StateInvocation('f2', {'notify': ['s1']})
		]),
		states.State('s3', [
			states.StateInvocation('f2', {'notify': ['s1']})
		]),
	])
	s = states.sort_states([sf])
	assert 's2' == s[0].name
	assert 's1' == s[1].name
	assert 's3' == s[2].name
	assert 's1' == s[3].name


def test_notify_defered_state():
	sf = states.LoadedStateFile('sf', [
		states.State('s1', [
			states.StateInvocation('f1', {'defer': True})
		]),
		states.State('s2', [
			states.StateInvocation('f2', {'notify': ['s1']})
		]),
		states.State('s3', [
			states.StateInvocation('f2', {'notify': ['s1']})
		]),
	])
	s = states.sort_states([sf])
	assert 's2' == s[0].name
	assert 's3' == s[1].name
	assert 's1' == s[2].name
