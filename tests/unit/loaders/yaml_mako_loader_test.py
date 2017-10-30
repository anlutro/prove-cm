import collections
from unittest import mock
from prove.loaders import yaml_mako


def test_load():
	with mock.patch('builtins.open', mock.mock_open(read_data='foo: ${vars.foo}')):
		data = yaml_mako.load('/path/to/yaml', {'foo': 'bar'})
	assert isinstance(data, dict)
	assert isinstance(data, collections.OrderedDict)
	assert {'foo': 'bar'} == data
