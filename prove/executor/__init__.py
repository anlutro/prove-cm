from contextlib import contextmanager
import logging

from lazy import lazy

import prove.config
import prove.catalog
import prove.util

LOG = logging.getLogger(__name__)


def command_with_sudo(command, shell='sh'):
	return 'sudo -n -- ' + prove.util.cmd_as_string([shell, '-c', command])


def parse_lsb_release(output):
	ret = {}
	for line in output.splitlines():
		if not ':' in line:
			continue
		key, val = line.strip().split(':', 1)
		ret[key.strip()] = val.strip()
	return ret


class SessionException(Exception):
	pass


class Session:
	def __init__(self, target, catalog, output):
		assert isinstance(target, prove.config.Target)
		self.target = target
		assert isinstance(catalog, prove.catalog.TargetCatalog)
		self.catalog = catalog
		self.output = output
		self.options = catalog.options
		self.info = SessionInfo(self)

	@property
	def is_dry_run(self):
		return self.options.get('dry_run', False)

	def connect(self):
		'''Connect to the remote host.'''
		raise NotImplementedError()

	def disconnect(self):
		'''Disconnect from the remote host.'''
		raise NotImplementedError()

	def run_action(self, action):
		'''Run an Action object through the session.'''
		action.run()

	def run_command(self, command, skip_sudo=False):
		'''Run a shell-like command through the session.'''
		command = prove.util.cmd_as_string(command)
		if not skip_sudo and self.options.get('sudo'):
			command = command_with_sudo(command)
		LOG.debug('running command: %r', command)
		return self._run_command(command)

	def _run_command(self, command):
		'''Run a shell-like command through the session. (Internal)'''
		raise NotImplementedError()

	def manage_file(self, remote_path, source=None, content=None):
		'''Get a file onto the remote system.'''
		if not source and not content:
			raise ValueError('must provide source or content!')

		if content:
			return self.write_to_file(content, remote_path)

		if source.startswith('http://') or source.startswith('https://'):
			if self.run_command('which wget').was_successful:
				return self.run_command('wget -nv {} -O {}'.format(source, remote_path)).was_successful
			elif self.run_command('which curl').was_successful:
				return self.run_command('curl {} -o {}'.format(source, remote_path)).was_successful
			raise Exception('curl or wget not found')

		if source.startswith('prove://'):
			source = source.replace('prove://', '')
			source = self.catalog.files[source]
			return self.upload_file(source, remote_path)

		if source.startswith('file://'):
			return self.run_command('cp {} {}'.format(source, remote_path)).was_successful

		raise Exception('Unknown file protocol: %s', source)

	def upload_file(self, source, remote_path):
		'''Upload a file from the prove master to the remote host.'''
		raise NotImplementedError()

	def write_to_file(self, content, remote_path):
		'''Write some contents to a file on the remote system.'''
		raise NotImplementedError()

	def download_file(self, remote_path):
		'''Get the contents of a file from the remote system.'''
		raise NotImplementedError()


class SessionInfo:
	def __init__(self, session):
		self.session = session

	@lazy
	def _lsb_release(self):
		result = self.session.run_command('lsb_release -a')
		if not result.was_successful:
			raise Exception(result.stderr)
		return parse_lsb_release(result.stdout)

	@property
	def distro(self):
		return self._lsb_release['Distributor ID']

	@property
	def distro_version(self):
		return self._lsb_release['Release']

	def program_exists(self, program):
		result = self.session.run_command(['which', program])
		return result.stdout.strip() if result.was_successful else False


class CommandResult:
	def __init__(self, exit_code, stdout, stderr):
		self.exit_code = exit_code
		self.stdout = stdout.strip()
		self.stderr = stderr.strip()

	@property
	def was_successful(self):
		return self.exit_code == 0

	@property
	def text(self):
		return '\n'.join([self.stdout, self.stderr])


class Executor:
	session_cls = Session

	def __init__(self, app):
		self.app = app

	@contextmanager
	def connect(self, target):
		try:
			session = self.get_session(target)
		except Exception as e:
			raise SessionException('could not start session for target %r' % target) from e

		LOG.info('connecting to target: %s', target.host)
		self.app.output.connect_start(target)

		try:
			session.connect()
			self.app.output.connect_success(target)
		except Exception as e:
			self.app.output.connect_failure(target)
			raise SessionException('could not connect to target %r' % target) from e

		try:
			yield session
		finally:
			LOG.info('diconnecting target: %s', target.host)
			session.disconnect()
			self.app.output.disconnected(target)

	def get_session(self, target):
		catalog = self.get_catalog(target)
		return self.session_cls(target, catalog, self.app.output)

	def get_catalog(self, target):
		LOG.debug('creating catalog for target: %s', target.host)
		catalog = self.app.get_target_catalog(target)
		LOG.debug('host catalog options: %s', catalog.options)
		LOG.debug('host catalog states: %s', catalog.states)
		LOG.debug('host catalog variables: %s', catalog.variables)
		return catalog
