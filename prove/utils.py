import collections
import os
import os.path
import yaml


def deep_dict_merge(old_dict, new_dict):
	old_dict = old_dict.copy()
	for key, value in new_dict.items():
		if key in old_dict and isinstance(old_dict[key], dict) and isinstance(value, dict):
			old_dict[key] = deep_dict_merge(old_dict[key], value)
		else:
			old_dict[key] = value
	return old_dict


def list_files(path):
	result_files = set()

	for root, _, files in os.walk(path):
		for file in files:
			result_files.add(os.path.join(root, file))

	return result_files


def snake_to_camel_case(string):
	return ''.join(s.title() for s in string.split('_'))


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
