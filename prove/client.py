import importlib
import os
import os.path
import yaml
import prove.runner


class Client():
	def __init__(self, config_path, args):
		with open(config_path) as f:
			self.config = yaml.load(f)
		if 'options' not in self.config:
			self.config['options'] = {}
		if 'root_path' not in self.config['options']:
			self.config['options']['root_path'] = os.path.dirname(config_path)

	def run(self):
		output_module = self.config.get('output_module', 'console')
		output_module = importlib.import_module('prove.output.' + output_module)

		roles = self.config.get('roles', {})
		roles.update(self.read_roles_from_files())

		targets = self.config.get('targets', [])
		for target in targets:
			variables = set()
			states = set()
			for role in target.get('roles', []):
				role = roles[role]
				for variable in role.get('variables', []):
					variables.add(variable)
				for state in role.get('states', []):
					states.add(state)

			for variable in target.get('variables', []):
				variables.add(variable)
			for state in target.get('states', []):
				states.add(state)

			target['variables'] = variables
			target['states'] = states

		global_variables = prove.get_variables(
			os.path.join(self.config['options']['root_path'], 'variables'),
			self.config.get('global_variables', [])
		)

		runner = prove.runner.Runner(
			self.config.get('options', {}),
			output_module,
			global_variables
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
