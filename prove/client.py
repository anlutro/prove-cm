import importlib
import os.path

import prove.runner
import yaml


class Client():
	@classmethod
	def from_config_file(cls, config_path, args):
		with open(config_path) as file:
			config = yaml.load(file)

		if 'options' not in config:
			config['options'] = {}
		if 'root_path' not in config['options']:
			config['options']['root_path'] = os.path.dirname(config_path)

		return cls(config, args)

	def __init__(self, config, args):
		self.config = config

		if 'options' not in self.config:
			self.config['options'] = {}

		self.root_path = self.config['options']['root_path']

	def run(self):
		output_module = self.config.get('output_module', 'console')
		output_module = importlib.import_module('prove.output.' + output_module)

		runner = prove.runner.Runner(
			self.config.get('options', {}),
			output_module,
			self.config.get('globals', {}),
		)
		runner.run(self.config.get('targets', []))
