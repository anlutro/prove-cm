import logging
import subprocess
import random

import prove.executor

log = logging.getLogger(__name__)


class Session(prove.executor.Session):
	def connect(self):
		pass

	def disconnect(self):
		pass

	def run_command(self, command):
		log.debug('Running command%s: `%s`',
			' with sudo' if self.options.get('sudo') else '',
			self._cmd_as_string(command),
		)

		if self.options.get('sudo'):
			command = self._cmd_as_string(command)
			heredoc_marker = 'PROVE_{}_EOF'.format(random.randint(10000, 99999))
			command = 'sudo {0} -c <<{1}\n{2}\n{1}'.format(
				self.options.get('shell', '/bin/sh'),
				heredoc_marker,
				self._cmd_as_string(command),
			)

		proc = subprocess.Popen(
			self._cmd_as_list(command),
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		stdout, stderr = proc.communicate()

		result = prove.executor.CommandResult(
			exit_code=proc.returncode,
			stdout=stdout.decode(),
			stderr=stderr.decode(),
		)

		return result

	def _upload_file(self, source, path):
		return self.run_command('cp {} {}'.format(source, path)).was_successful


class Executor(prove.executor.Executor):
	session_cls = Session
