import logging
import subprocess

import prove.executor
import prove.util

LOG = logging.getLogger(__name__)


class Session(prove.executor.Session):
	def connect(self):
		pass

	def disconnect(self):
		pass

	def _run_command(self, command):
		proc = subprocess.Popen(
			prove.util.cmd_as_list(command),
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

	def upload_file(self, source, path):
		return self.run_command('cp {} {}'.format(source, path)).was_successful

	def write_to_file(self, content, path):
		with open(path, 'w+') as filehandle:
			filehandle.write(content)


class Executor(prove.executor.Executor):
	session_cls = Session
