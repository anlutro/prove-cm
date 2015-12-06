import os
import os.path
import yaml
import prove
import mako.template
import paramiko
import importlib


def normalize_state_data(state_data):
	if not isinstance(state_data, list):
		state_data_list = []
		for state_fn, state_args in state_data.items():
			state_dict = collections.OrderedDict({'fn': state_fn})
			state_dict.update(state_args)
			state_data_list.append(state_dict)
		state_data = state_data_list

	return state_data


def get_states_yaml(state_yaml):
	states = []
	for state_id, state_data in state_yaml.items():
		state_data = normalize_state_data(state_data)
		for state_call in state_data:
			state_fn = state_call.pop('fn')
			state_args = state_call
			states.append((state_id, state_fn, state_args))
	return states


def get_state_cls(state_fn):
	state_mod, state_fn = state_fn.rsplit('.', 1)

	try:
		state_module = importlib.import_module('prove.states.' + state_mod)
	except ImportError:
		raise ProveError('No state module named {}'.format(state_mod))

	try:
		state_cls = getattr(state_module, state_fn)
	except AttributeError:
		raise ProveError('State module {} has no function {}'.format(state_mod, state_fn))

	if hasattr(state_module, '__hidden__') and state_fn in state_module.__hidden__:
		raise ProveError('State module {} function {} is not public'.format(state_mod, state_fn))

	if state_fn.startswith('_'):
		raise ProveError('State module function {}.{} is private'.format(state_mod, state_fn))

	return state_cls


class HostRunner():
	def __init__(self, ssh_client, options, output_module, variables):
		self.ssh_client = ssh_client
		self.options = options
		self.output = output_module
		self.variables = variables
		self.num_succeeded_states = 0
		self.num_failed_states = 0

	def run(self):
		kwargs = {}
		if self.options.get('username'):
			kwargs['username'] = self.options['username']
		if self.options.get('password'):
			kwargs['password'] = self.options['password']

		self.output.start_connect(self.options['host'])
		self.ssh_client.connect(self.options['host'], **kwargs)
		self.output.finish_connect()

		for state_file_name in self.options.get('states', []):
			self.variables['state_file'] = state_file_name
			self.run_states(state_file_name)

		self.output.finish_run(self.num_succeeded_states, self.num_failed_states)

	def run_states(self, state_file_name):
		state_file = os.path.join(self.options['root_path'], 'states', state_file_name)

		for ext in ('yml.mako', 'yaml.mako', 'yml', 'yaml', 'py'):
			state_file_check = '{}.{}'.format(state_file, ext)
			if os.path.isfile(state_file_check):
				state_file = state_file_check
				break
		else:
			return

		states = self.get_states(state_file)
		for state_id, state_fn, state_args in states:
			self.output.start_state(state_id, state_fn)

			try:
				state_cls = get_state_cls(state_fn)
				state_obj = state_cls(self.ssh_client)
				result, comment = state_obj.run(**state_args)
			except prove.ProveError as e:
				self.output.state_error(e)
				self.num_failed_states += 1
				continue

			self.output.finish_state(result, comment)
			if result:
				self.num_succeeded_states += 1
			else:
				self.num_failed_states += 1

	def get_states(self, state_file):
		if state_file.endswith('.yml.mako') or state_file.endswith('.yaml.mako'):
			with open(state_file, 'r') as f:
				yaml_str = mako.template.Template(f.read()).render(**self.variables)
			state_data = yaml.load(yaml_str, prove.utils.CustomYAMLLoader)
			return get_states_yaml(state_data)

		elif state_file.endswith('.yml') or state_file.endswith('.yaml'):
			with open(state_file, 'r') as f:
				state_data = yaml.load(f, prove.utils.CustomYAMLLoader)
			return get_states_yaml(state_data)

		else:
			raise ValueError('Unknown state extension: "{}"'.format(state_file))


class Runner():
	def __init__(self, options, output_module, global_variables=None):
		self.options = options
		self.output = output_module
		self.global_variables = global_variables or {}

	def run(self, targets):
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		for host_options in targets:
			new_host_options = self.options.copy()
			new_host_options.update(host_options)
			host_options.update(new_host_options)
			del new_host_options

			variables = self.global_variables.copy()
			variables.update(prove.get_variables(
				os.path.join(self.options['root_path'], 'variables'),
				host_options.get('variables', [])
			))

			host_runner = HostRunner(ssh_client, host_options, self.output, variables)
			host_runner.run()

