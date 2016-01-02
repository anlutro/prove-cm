import prove.util


def test_deep_dict_merge():
	d1 = {'a': {'b': 'c'}}
	d2 = {'a': {'b': 'd', 'e': 'f'}}
	merged = prove.util.deep_dict_merge(d1, d2)
	assert 'd' == merged['a']['b']
	assert 'f' == merged['a']['e']


def test_case_convert():
	assert 'Test' == prove.util.snake_to_camel_case('test')
	assert 'TestTest' == prove.util.snake_to_camel_case('test_test')
