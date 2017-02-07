import pytest
from prove.states import State, StateFuncCall
from prove.states.graph import generate_graph

def test_singular_requirements():
	states = [
		State('a', [StateFuncCall('test.noop', {})]),
		State('b', [StateFuncCall('test.noop', {'requires': ['a']})]),
		State('c', [StateFuncCall('test.noop', {'requires': ['a']})]),
		State('d', [StateFuncCall('test.noop', {'requires': ['c']})]),
	]
	graph = generate_graph(states)
	assert 'a -> (b + (c -> d))' == str(graph)


@pytest.mark.skip(reason='not implemented yet')
def test_mutliple_requirements():
	states = [
		State('a', [StateFuncCall('test.noop', {})]),
		State('b', [StateFuncCall('test.noop', {})]),
		State('c', [StateFuncCall('test.noop', {'requires': ['a', 'b']})]),
		State('d', [StateFuncCall('test.noop', {'requires': ['c']})]),
		State('e', [StateFuncCall('test.noop', {'requires': ['c']})]),
		State('f', [StateFuncCall('test.noop', {'requires': ['d', 'e']})]),
	]
	graph = generate_graph(states)
	assert '(a+b) -> c -> (d+e) -> f' == str(graph)


def test_multiple_parallel():
	states = [
		State('a', [StateFuncCall('test.noop', {})]),
		State('b', [StateFuncCall('test.noop', {})]),
		State('c', [StateFuncCall('test.noop', {'requires': ['a']})]),
		State('d', [StateFuncCall('test.noop', {'requires': ['b']})]),
		State('e', [StateFuncCall('test.noop', {'requires': ['c']})]),
		State('f', [StateFuncCall('test.noop', {'requires': ['d']})]),
	]
	graph = generate_graph(states)
	assert 'a -> c -> e\nb -> d -> f' == str(graph)
