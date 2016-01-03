import argparse
import importlib
import os
import os.path

import prove.client
import prove.util


def _locate_config():
	search_dir = os.getcwd()
	while search_dir != '/':
		path = os.path.join(search_dir, 'prove.yml')
		if os.path.isfile(path):
			return path
		search_dir = os.path.dirname(search_dir)
	raise Exception('Could not locate prove.yml')


class ConsoleClient(prove.client.Client):
	def __init__(self, args=None):
		parser = argparse.ArgumentParser(description="Prove - a configuration manager")
		parser.add_argument('action', choices=['states', 'cmd', 'ping'],
			help="Which action to run")
		parser.add_argument('-c', '--config',
			help="Path to config file")
		parser.add_argument('-d', '--dry-run', action='store_true',
			help="Do a dry/test run")
		parser.add_argument('-l', '--log-level',
			help="Set the log level")
		parser.add_argument('--log-path',
			help="Set the log path")
		parser.add_argument('-o', '--output', '--out',
			help="Choose output module")
		parser.add_argument('action_args', nargs='*',
			help="Arguments to the action function")
		self.args = parser.parse_args(args)

	def get_config(self):
		config_path = self.args.config or _locate_config()
		config = self.parse_configfile(config_path)

		# set some sensible defaults
		if 'options' not in config:
			config['options'] = {}
		if 'root_dir' not in config['options']:
			config['options']['root_dir'] = os.path.dirname(config_path)

		# override with command-line args
		config['options']['dry_run'] = self.args.dry_run
		if self.args.log_level is not None:
			config['options']['log_level'] = self.args.log_level
		if self.args.log_path is not None:
			config['options']['log_path'] = self.args.log_path
		if self.args.output is not None:
			config['options']['output'] = self.args.output

		return config

	def get_action(self):
		action_module = 'prove.actions.' + self.args.action
		action_module = importlib.import_module(action_module)
		action_class = prove.util.snake_to_camel_case(self.args.action)
		action_class = getattr(action_module, action_class + 'Action')
		return action_class(self.args.action_args)


def main():
	ConsoleClient().main()
