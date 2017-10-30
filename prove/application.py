import fnmatch
import importlib
import logging

import prove.operations
import prove.config
import prove.catalog.locator
import prove.util

LOG = logging.getLogger(__name__)


class Application:
	def __init__(self, options, catalog, targets, output):
		assert isinstance(options, prove.config.Options)
		self.options = options
		assert isinstance(catalog, prove.catalog.Catalog)
		self.catalog = catalog
		self.targets = targets
		self.output = output
		self.executors = {}

	@classmethod
	def from_config(cls, config):
		assert isinstance(config, dict)
		options = prove.config.Options(config['options'])

		catalog = prove.catalog.Catalog.from_options_and_config(options, config)

		groups = [
			prove.config.Group(**group)
			for group in config.get('groups', [])
		]

		targets = []
		for target in config.get('targets', []):
			target = prove.config.Target(**target)
			for group in groups:
				if group.matches(target):
					group.merge_into(target)
			targets.append(target)

		output_module = 'prove.output.' + options.get('output', 'console')
		LOG.debug('importing output module: %s', output_module)
		output = importlib.import_module(output_module)

		return cls(options, catalog, targets, output)

	def run_command(self, command):
		assert isinstance(command, prove.operations.Command)
		LOG.info('Running command: %s', command.__class__.__name__)
		command.run(self.filter_targets())

	def filter_targets(self):
		targets = []
		target_patterns = self.options.get('_target_patterns', [])
		target_groups = set(self.options.get('_target_groups', []))

		for target in self.targets:
			if target_patterns:
				if not any((
					fnmatch.fnmatch(target.name, pattern)
					for pattern in target_patterns
				)):
					LOG.debug('target %s matches none of the target patterns, skipping',
						target)
					continue

			if target_groups:
				if not set(target.groups).intersection(target_groups):
					LOG.debug('target %s matches none of the target groups, skipping',
						target)
					continue

			targets.append(target)

		return targets

	def get_target_catalog(self, target):
		return self.catalog.make_target_catalog(target)

	def get_target_executor(self, target):
		assert isinstance(target, prove.config.Target)
		ex_type = target.options.get('executor', self.options['executor'])
		if ex_type not in self.executors:
			self.executors[ex_type] = self._make_executor(ex_type)
		LOG.info('Using executor type: %s', ex_type)
		return self.executors[ex_type]

	def make_session(self, target):
		return self.get_target_executor(target).get_session(target)

	def executor_connect(self, target):
		return self.get_target_executor(target).connect(target)

	def _make_executor(self, module):
		executor_module = importlib.import_module('prove.executor.' + module)
		return getattr(executor_module, 'Executor')(self)
