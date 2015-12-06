import importlib
import os
import os.path
import yaml
import prove.runner
import prove.environment


class Client():
	@classmethod
	def from_config_file(cls, config_path, args):
		with open(config_path) as f:
			config = yaml.load(f)

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

	def read_roles_from_files(self):
		roles_dir = os.path.join(self.config['options']['root_path'], 'roles')
		role_files = [f for f in os.listdir(roles_dir) if os.path.isfile(os.path.join(roles_dir, f))]
		roles = {}
		for role_file in role_files:
			full_path = os.path.join(roles_dir, role_file)
			if role_file.endswith('.yml') or role_file.endswith('.yaml'):
				with open(full_path) as f:
					roles[role_file.split('.')[0]] = yaml.load(f)
			if role_file.endswith('.json'):
				with open(full_path) as f:
					roles[role_file.split('.')[0]] = json.load(f)
		return roles
