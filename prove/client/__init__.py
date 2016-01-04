import yaml

from prove import setup_logging
from prove.application import Application


class Client:
	def main(self):
		config = self.get_config()
		setup_logging(config.get('options', {}))

		app = Application.from_config(config)
		app.run_action(self.get_action())

	def parse_configfile(self, path):
		with open(path) as file:
			return yaml.load(file)

	def get_config(self):
		raise NotImplementedError()

	def get_action(self):
		raise NotImplementedError()
