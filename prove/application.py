import importlib
import logging

import prove.actions
import prove.config
import prove.locator
import prove.util

log = logging.getLogger(__name__)


class Application:
	def __init__(self, options, env, hosts, output):
		assert isinstance(options, prove.config.Options)
		self.options = options
		assert isinstance(env, prove.environment.Environment)
		self.global_env = env
		self.hosts = hosts
		self.output = output
		self.executors = {}

	@classmethod
	def from_config(cls, config):
		assert isinstance(config, dict)
		options = prove.config.Options(config['options'])

		env = prove.environment.Environment.from_options_and_config(options, config)

		groups = {
			group['name']: prove.config.Group(**group)
			for group in config.get('groups', [])
		}

		targets = []
		for target in config.get('targets', []):
			target = prove.config.Target(**target)
			for group_name, group in groups.items():
				if group.matches(target):
					group.merge_into(target)
			targets.append(target)

		output_module = 'prove.output.' + options.get('output', 'console')
		log.debug('importing output module: %s', output_module)
		output = importlib.import_module(output_module)

		return cls(options, env, targets, output)

	def run_command(self, command):
		assert isinstance(command, prove.actions.Command)
		log.info('Running command: %s', command.__class__.__name__)
		command.run(self)

	def get_host_env(self, host):
		return self.global_env.make_host_env(host)

	def executor_connect(self, host):
		assert isinstance(host, prove.config.HostConfig)
		ex_type = host.options.get('executor', self.options['executor'])
		if ex_type not in self.executors:
			self.executors[ex_type] = self._make_executor(ex_type)
		log.info('Using executor type: %s', ex_type)
		return self.executors[ex_type].connect(host)

	def _make_executor(self, module):
		executor_module = importlib.import_module('prove.executor.' + module)
		return getattr(executor_module, 'Executor')(self)
