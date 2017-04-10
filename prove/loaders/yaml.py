from prove.loaders import LoaderException
from collections import OrderedDict
import yaml


def _construct_mapping(loader, node):
	loader.flatten_mapping(node)
	return OrderedDict(loader.construct_pairs(node))


class OrderedLoader(yaml.Loader):
	pass


OrderedLoader.add_constructor(
	yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
	_construct_mapping)


def _ordered_load(stream):
	try:
		return yaml.load(stream, OrderedLoader)
	except yaml.scanner.ScannerError as e:
		raise LoaderException('error while parsing %r' % stream) from e


def supports(filename):
	return filename.endswith('.yml') or filename.endswith('.yaml')


def load(path, variables=None):
	with open(path, 'r') as file:
		return _ordered_load(file)
