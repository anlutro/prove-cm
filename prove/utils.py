import collections
import os
import os.path
import yaml


def list_files(path):
	result_files = set()

	for root, dirs, files in os.walk(path):
		for f in files:
			result_files.add(os.path.join(root, f))

	return result_files


class CustomYAMLLoader(yaml.Loader):
	def construct_yaml_map(self, node):
		data = collections.OrderedDict()
		yield data
		value = self.construct_mapping(node)
		data.update(value)

	def construct_mapping(self, node, deep=False):
		if isinstance(node, yaml.MappingNode):
			self.flatten_mapping(node)
		else:
			raise yaml.constructor.ConstructorError(None, None,
				'expected a mapping node, but found %s' % node.id, node.start_mark)

		mapping = collections.OrderedDict()
		for key_node, value_node in node.value:
			key = self.construct_object(key_node, deep=deep)
			try:
				hash(key)
			except TypeError as exc:
				raise yaml.constructor.ConstructorError('while constructing a mapping',
					node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
			value = self.construct_object(value_node, deep=deep)
			mapping[key] = value
		return mapping
