import logging
import socket
import subprocess

import prove.executor

log = logging.getLogger(__name__)


class Connection(prove.executor.Connection):
	def connect(self):
		pass

	def disconnect(self):
		pass

	def run_command(self, command):
		log.debug('Running command: `%s`', self._cmd_as_string(command))

		p = subprocess.Popen(
			self._cmd_as_list(command),
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		stdout, stderr = p.communicate()

		result = prove.executor.CommandResult(
			exit_code=p.returncode,
			stdout=stdout.decode(),
			stderr=stderr.decode(),
		)

		return result


class Executor(prove.executor.Executor):
	connection_cls = Connection
