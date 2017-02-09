import pytest
from prove.states import State, StateFuncCall
from prove.states.graph import generate_graph


def _state(name, requires=None):
	kwargs = {'requires': requires} if requires else {}
	return State(name, [StateFuncCall('test.noop', kwargs)])


def test_dependency():
	graph = generate_graph([_state('a'), _state('b', ['a'])])
	assert 'a -> b' == str(graph)


def test_multiple_dependents():
	graph = generate_graph([
		_state('a'),
		_state('b', ['a']),
		_state('c', ['a']),
	])
	assert 'a -> (b+c)' == str(graph)


@pytest.mark.xfail(reason='not implemented yet')
def test_branching():
	graph = generate_graph([
		_state('a'),
		_state('b', ['a']),
		_state('c', ['a']),
		_state('d', ['b']),
		_state('e', ['c']),
	])
	assert 'a -> (b -> d) + (c -> e)' == str(graph)


def test_multiple_dependencies():
	graph = generate_graph([
		_state('a'),
		_state('b',),
		_state('c', ['a', 'b']),
	])
	assert '(a+b) -> c' == str(graph)


def test_mutliple_requirements():
	graph = generate_graph([
		_state('a'),
		_state('b'),
		_state('c', ['a', 'b']),
		_state('d', ['c']),
		_state('e', ['c']),
		_state('f', ['d', 'e']),
	])
	assert '(a+b) -> c -> (d+e) -> f' == str(graph)


def test_shared_branches():
	graph = generate_graph([
		_state('a'),
		_state('b', ['a']),
		_state('c', ['a']),
		_state('d', ['a']),
		_state('e', ['b', 'c']),
		_state('f', ['c', 'd']),
	])
	assert 'a -> (b+c+d) -> (e+f)' == str(graph)


def test_multiple_parallel():
	graph = generate_graph([
		_state('a'),
		_state('b'),
		_state('c', ['a']),
		_state('d', ['b']),
		_state('e', ['c']),
		_state('f', ['d']),
	])
	assert 'a -> c -> e\nb -> d -> f' == str(graph)
