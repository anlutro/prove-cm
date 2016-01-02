import yaml
from collections import OrderedDict


def _construct_mapping(loader, node):
	loader.flatten_mapping(node)
	return OrderedDict(loader.construct_pairs(node))


class OrderedLoader(yaml.Loader):
	pass


OrderedLoader.add_constructor(
	yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
	_construct_mapping)


def _ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
	return yaml.load(stream, OrderedLoader)


def supports(filename):
	return filename.endswith('.yml') or filename.endswith('.yaml')


def load(path, variables=None):
	with open(path, 'r') as f:
		return _ordered_load(f)
