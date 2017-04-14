from prove.states import State, StateFuncCall, StateCollection, StateMap


def test_state_requires_accumulates_invocation_requires():
	s = State('s1', [
		StateFuncCall('f1', {'requires': ['s2']}),
		StateFuncCall('f2', {'requires': ['s3']}),
	])
	assert ['s2', 's3'] == s.requires


def test_state_collection_depends():
	states = [
		State('s1', []),
		State('s2', [
			StateFuncCall('f1', {'requires': ['s1']})
		]),
	]
	coll = StateCollection(states)

	assert isinstance(coll.depends, StateMap)
	assert 1 == len(coll.depends)
	assert isinstance(coll.depends['s2'], list)
	assert 1 == len(coll.depends['s2'])
	assert isinstance(coll.depends['s2'][0], State)
	assert coll.depends['s2'][0].name == 's1'

	assert isinstance(coll.rdepends, StateMap)
	assert 1 == len(coll.rdepends)
	assert isinstance(coll.rdepends['s1'], list)
	assert 1 == len(coll.rdepends['s1'])
	assert isinstance(coll.rdepends['s1'][0], State)
	assert coll.rdepends['s1'][0].name == 's2'
