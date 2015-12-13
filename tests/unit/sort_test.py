import prove.sort


def test_high_priority_comes_before_low_priority():
	states = prove.sort.sort_states([
		('a', None, {'_priority': 2}),
		('b', None, {'_priority': 1}),
	])
	assert 'b' == states[0][0]
	assert 'a' == states[1][0]


def test_priority_comes_before_no_priority():
	states = prove.sort.sort_states([
		('a', None, {}),
		('b', None, {'_priority': 1}),
	])
	assert 'b' == states[0][0]
	assert 'a' == states[1][0]


def test_priority_last_comes_after_no_priority():
	states = prove.sort.sort_states([
		('a', None, {'_priority': 'last'}),
		('b', None, {}),
	])
	assert 'b' == states[0][0]
	assert 'a' == states[1][0]


def test_priority_first_comes_before_no_priority():
	states = prove.sort.sort_states([
		('a', None, {}),
		('b', None, {'_priority': 'first'}),
	])
	assert 'b' == states[0][0]
	assert 'a' == states[1][0]


def test_sort_states_complex():
	states = prove.sort.sort_states([
		('e', None, {'_priority': 'last'}),
		('d', None, {}),
		('c', None, {'_priority': 2}),
		('b', None, {'_priority': 1}),
		('a', None, {'_priority': 'first'}),
	])
	assert 'a' == states[0][0]
	assert 'b' == states[1][0]
	assert 'c' == states[2][0]
	assert 'd' == states[3][0]
	assert 'e' == states[4][0]


def test_state_with_dependency_is_ran_after_the_dependency():
	states = prove.sort.sort_states([
		('a', None, {'_require': 'b'}),
		('b', None, {}),
	])
	assert 'b' == states[0][0]
	assert 'a' == states[1][0]


def test_nested_dependencies_are_ran_in_order():
	states = prove.sort.sort_states([
		('a', None, {'_require': 'b'}),
		('b', None, {'_require': 'c'}),
		('c', None, {}),
	])
	assert 'c' == states[0][0]
	assert 'b' == states[1][0]
	assert 'a' == states[2][0]


def test_state_with_depenceny_and_order_are_ran_in_order():
	states = prove.sort.sort_states([
		('a', None, {'_require': 'b'}),
		('b', None, {'_priority': 2}),
		('c', None, {'_require': 'd'}),
		('d', None, {'_priority': 1}),
	])
	assert 'd' == states[0][0]
	assert 'c' == states[1][0]
	assert 'b' == states[2][0]
	assert 'a' == states[3][0]
