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