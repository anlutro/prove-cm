import argparse
import importlib
import logging
import os
import os.path
import sys

import prove.state.runner
import yaml


def setup_logging(config):
	log_level = logging.INFO
	# read the logging level from the config file, defaulting to INFO
	if 'log_level' in config:
		log_level = getattr(logging, config['log_level'].upper())

	# set the level
	root = logging.getLogger()
	root.setLevel(log_level)

	log_path = config.get('log_path')

	if not log_path or log_path == 'stdout':
		handler = logging.StreamHandler(sys.stdout)
	elif log_path == 'stderr':
		handler = logging.StreamHandler(sys.stderr)
	elif log_path:
		handler = logging.StreamHandler(log_path)

	handler.setLevel(log_level)

	# define the logging format
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
	handler.setFormatter(formatter)

	# add the logging handler for all loggers
	root.addHandler(handler)


def main():
	parser = argparse.ArgumentParser(description='Prove - a configuration manager')
	parser.add_argument('command', choices=['states'], help='Which command to run')
	parser.add_argument('-c', '--config', help='Path to config file')
	args = parser.parse_args()

	with open(args.config) as file:
		config = yaml.load(file)

	if 'options' not in config:
		config['options'] = {}
	if 'root_path' not in config['options']:
		config['options']['root_path'] = os.path.dirname(args.config)

	setup_logging(config['options'])

	output_module = config.get('output_module', 'console')
	output_module = importlib.import_module('prove.output.' + output_module)

	if args.command == 'states':
		runner = prove.state.runner.Runner(
			config.get('options', {}),
			output_module,
			config.get('globals', {}),
		)
		runner.run(config.get('targets', []))


if __name__ == '__main__':
	main()
