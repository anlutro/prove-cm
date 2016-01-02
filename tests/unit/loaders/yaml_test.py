import collections
from unittest import mock
from prove.loaders import yaml


def test_load():
	with mock.patch('builtins.open', mock.mock_open(read_data='foo: bar')):
		data = yaml.load('/path/to/yaml')
	assert isinstance(data, dict)
	assert isinstance(data, collections.OrderedDict)
	assert {'foo': 'bar'} == data
