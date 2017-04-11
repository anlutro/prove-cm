import os
import os.path
import shlex


def cmd_as_list(command):
	if not isinstance(command, list):
		command = shlex.split(command)
	if len(command) == 1 and ' ' in command[0]:
		command = shlex.split(command[0])
	return command


def cmd_as_string(command):
	if isinstance(command, list):
		command = ' '.join([shlex.quote(part) for part in command])
	return command


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


def list_subdirs(path):
	if not os.path.exists(path):
		return []
	return next(os.walk(path))[1]


def snake_to_camel_case(string):
	return ''.join(s.title() for s in string.split('_'))


def indent_string(string, spaces):
	return '\n'.join((((' ' * spaces) + line) for line in string.splitlines()))


def format_result(comment=None, comments=None, stdout=None, stderr=None, indent=2):
	comment = comment or ''
	if comments:
		comment += '\n' + '\n'.join(comments)
	if stdout:
		comment += '\nsystem stdout:\n' + indent_string(stdout, indent)
	if stderr:
		comment += '\nsystem stderr:\n' + indent_string(stderr, indent)
	return comment.strip()
