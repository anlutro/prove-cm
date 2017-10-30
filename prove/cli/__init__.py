import os
import os.path
import yaml

import allib.logging
from prove.application import Application


def _locate_config():
	search_dir = os.getcwd()
	while search_dir != '/':
		path = os.path.join(search_dir, 'prove.yml')
		if os.path.isfile(path):
			return path
		search_dir = os.path.dirname(search_dir)
	raise Exception('Could not locate prove.yml')


def _read_config(config_path):
	with open(config_path) as file:
		return yaml.load(file)


class AbstractClient:
	def __init__(self, args):
		self.args = args

	def main(self):
		raise NotImplementedError()

	def make_app(self):
		config = self.read_config()
		return Application.from_config(config)

	def read_config(self):
		config = self.get_config()
		opts = config.get('options', {})
		allib.logging.setup_logging(
			log_file=opts.get('log_path'),
			log_level=opts.get('log_level'),
			colors=True,
		)
		return config

	def get_config(self):
		config_path = self.args.config or _locate_config()
		config = _read_config(config_path)

		# set some sensible defaults
		if 'options' not in config:
			config['options'] = {}
		if 'root_dir' not in config['options']:
			config['options']['root_dir'] = os.path.dirname(config_path)

		def normalize_path(path):
			path = os.path.expanduser(path)
			if not os.path.isabs(path):
				path = os.path.join(config['options']['root_dir'], path)
			return path

		for key in config['options'].get('ssl', {}).keys():
			config['options']['ssl'][key] = normalize_path(config['options']['ssl'][key])

		for target in config.get('targets', []):
			if 'ssh_key' in target:
				target['ssh_key'] = normalize_path(target['ssh_key'])

		# override with command-line args
		if self.args.log_level is not None:
			config['options']['log_level'] = self.args.log_level
		if self.args.log_path is not None:
			config['options']['log_path'] = self.args.log_path

		return config


class SingleCommandClient(AbstractClient):
	def main(self):
		app = self.make_app()
		cmd = self.get_command(app)
		app.run_command(cmd)

	def get_command(self, app):
		raise NotImplementedError()
