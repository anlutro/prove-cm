import collections
import prove
import prove.environment
import prove.utils
import paramiko
import importlib


def normalize_state_data(state_file_data):
	states = []
	for state_id, state_data in state_file_data.items():
		if not isinstance(state_data, list):
			state_data_list = []
			for state_fn, state_args in state_data.items():
				state_dict = collections.OrderedDict({'fn': state_fn})
				state_dict.update(state_args)
				state_data_list.append(state_dict)
			state_data = state_data_list
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
	def __init__(self, env, ssh_client, options, output_module):
		self.env = env
		self.ssh_client = ssh_client
		self.options = options
		self.output = output_module

		self.num_succeeded_states = 0
		self.num_failed_states = 0

	def run(self):
		kwargs = {}
		if self.options.get('username'):
			kwargs['username'] = self.options['username']
		if self.options.get('password'):
			kwargs['password'] = self.options['password']

		self.output.rendering_states(self.options['host'])
		state_files = self.env.get_states()

		self.output.start_connect()
		self.ssh_client.connect(self.options['host'], **kwargs)
		self.output.finish_connect()

		for states in state_files.values():
			for state_id, state_fn, state_args in normalize_state_data(states):
				self.run_state(state_id, state_fn, state_args)

		self.output.finish_run(self.num_succeeded_states, self.num_failed_states)

	def run_state(self, state_id, state_fn, state_args):
		self.output.start_state(state_id, state_fn)

		try:
			state_cls = get_state_cls(state_fn)
			state_obj = state_cls(self.ssh_client)
			result, comment = state_obj.run(**state_args)
		except prove.ProveError as e:
			self.output.state_error(e)
			self.num_failed_states += 1
			return

		self.output.finish_state(result, comment)
		if result:
			self.num_succeeded_states += 1
		else:
			self.num_failed_states += 1


class Runner():
	def __init__(self, options, output_module, global_variables=None):
		self.env = prove.environment.Environment.from_path(
			options['root_path'],
			options.get('loaders', ['yaml_mako', 'yaml', 'json']),
			global_variables,
		)
		self.options = options
		self.output = output_module

	def run(self, targets):
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		for host_options in targets:
			host_options = prove.utils.deep_dict_merge(self.options, host_options)

			host_env = self.env.make_host_env(
				host_options.get('roles', []),
				host_options.get('variables', []),
				host_options.get('states', []),
			)
			host_runner = HostRunner(host_env, ssh_client, host_options, self.output)
			host_runner.run()
