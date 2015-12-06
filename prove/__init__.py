import base64
import collections
import importlib
import os
import os.path
import paramiko
import prove.utils
import prove.client
import sys
import yaml


class ProveError(BaseException):
	pass


def get_variables(root_path, variable_files):
	variables = {}
	for variable_file in variable_files:
		variable_file = os.path.join(root_path, variable_file)
		for ext in ('yml', 'yaml'):
			variable_file_check = '{}.{}'.format(variable_file, ext)
			if os.path.isfile(variable_file_check):
				variable_file = variable_file_check
				break
		else:
			continue
		if variable_file.endswith('.yml') or variable_file.endswith('.yaml'):
			with open(variable_file, 'r') as f:
				variables.update(yaml.load(f))
		else:
			raise ProveError('Unknown variable file type: ' + variable_file)
	return variables


def main():
	args = sys.argv[1:]

	for arg in args:
		if not arg.startswith('-'):
			config_path = arg
			args.remove(config_path)
			break
	else:
		config_path = os.path.join(os.getcwd(), 'prove.yml')

	prove.client.Client.from_config_file(config_path, args).run()


if __name__ == '__main__':
	main()
