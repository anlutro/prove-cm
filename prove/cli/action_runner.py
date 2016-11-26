import argparse
import importlib

import prove.cli
import prove.util


class ActionRunner(prove.cli.SingleCommandClient):
	def __init__(self, args=None):
		parser = argparse.ArgumentParser(description="Prove - a configuration manager")
		parser.add_argument('command', help="Which command to run")
		parser.add_argument('-c', '--config',
			help="Path to config file")
		parser.add_argument('-d', '--dry-run', action='store_true',
			help="Do a dry/test run")
		parser.add_argument('-g', '--groups',
			help="Choose which groups to run against. Accepts multiple, comma-separated.")
		parser.add_argument('-t', '--targets',
			help="Choose which targets to run against. Accepts a glob pattern. Accepts multiple, comma-separated.")
		parser.add_argument('-l', '--log-level',
			help="Set the log level")
		parser.add_argument('--log-path',
			help="Set the log path")
		parser.add_argument('-o', '--output', '--out',
			help="Choose output module")
		parser.add_argument('command_args', nargs='*',
			help="Arguments to the command function")
		super().__init__(parser.parse_args(args))

	def get_config(self):
		config = super().get_config()

		config['options']['dry_run'] = self.args.dry_run
		if self.args.output is not None:
			config['options']['output'] = self.args.output

		if self.args.targets:
			config['options']['_target_patterns'] = self.args.targets.split(',')

		if self.args.groups:
			config['options']['_target_groups'] = self.args.groups.split(',')

		return config

	def get_command(self, app):
		cmd_module = 'prove.actions.' + self.args.command.replace('-', '_')
		cmd_module = importlib.import_module(cmd_module)
		cmd_class = prove.util.snake_to_camel_case(self.args.command)
		cmd_class = getattr(cmd_module, cmd_class + 'Command')
		return cmd_class(app, self.args.command_args)


def main():
	ActionRunner().main()


if __name__ == '__main__':
	main()
