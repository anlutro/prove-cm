import prove.utils


def test_deep_dict_merge():
	d1 = {'a': {'b': 'c'}}
	d2 = {'a': {'b': 'd', 'e': 'f'}}
	merged = prove.utils.deep_dict_merge(d1, d2)
	assert merged['a']['b'] == 'd'
	assert merged['a']['e'] == 'f'
