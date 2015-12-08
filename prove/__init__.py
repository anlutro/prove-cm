import importlib
import os
import os.path
import sys

import prove.runner
import yaml


def main():
	args = sys.argv[1:]

	for arg in args:
		if not arg.startswith('-'):
			config_path = arg
			args.remove(config_path)
			break
	else:
		config_path = os.path.join(os.getcwd(), 'prove.yml')

	with open(config_path) as file:
		config = yaml.load(file)

	if 'options' not in config:
		config['options'] = {}
	if 'root_path' not in config['options']:
		config['options']['root_path'] = os.path.dirname(config_path)

	output_module = config.get('output_module', 'console')
	output_module = importlib.import_module('prove.output.' + output_module)

	runner = prove.runner.Runner(
		config.get('options', {}),
		output_module,
		config.get('globals', {}),
	)
	runner.run(config.get('targets', []))


if __name__ == '__main__':
	main()
