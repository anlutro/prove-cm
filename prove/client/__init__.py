import os
import os.path
import yaml

from prove import setup_logging
from prove.application import Application


def _locate_config():
	search_dir = os.getcwd()
	while search_dir != '/':
		path = os.path.join(search_dir, 'prove.yml')
		if os.path.isfile(path):
			return path
		search_dir = os.path.dirname(search_dir)
	raise Exception('Could not locate prove.yml')


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
		setup_logging(config.get('options', {}))
		return config

	def get_config(self):
		config_path = self.args.config or _locate_config()
		with open(config_path) as file:
			config = yaml.load(file)

		# set some sensible defaults
		if 'options' not in config:
			config['options'] = {}
		if 'root_dir' not in config['options']:
			config['options']['root_dir'] = os.path.dirname(config_path)

		# override with command-line args
		if self.args.log_level is not None:
			config['options']['log_level'] = self.args.log_level
		if self.args.log_path is not None:
			config['options']['log_path'] = self.args.log_path

		return config


class SingleCommandClient(AbstractClient):
	def main(self):
		app = self.make_app()
		app.run_command(self.get_command())

	def get_command(self):
		raise NotImplementedError()
