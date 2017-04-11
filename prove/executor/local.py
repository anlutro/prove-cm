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

	def _run_command(self, command, shell=True):
		if not shell:
			command = prove.util.cmd_as_list(command)

		proc = subprocess.Popen(
			command,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			shell=shell,
		)
		stdout, stderr = proc.communicate()

		result = prove.executor.CommandResult(
			exit_code=proc.returncode,
			stdout=stdout.decode(),
			stderr=stderr.decode(),
		)

		return result

	def upload_file(self, source, path):
		LOG.debug('uploading file %r to %r', source, path)
		return self.run_command(['cp', source, path]).was_successful

	def write_to_file(self, content, path):
		LOG.debug('downloading %d characters to file %r', len(content), path)
		with open(path, 'w+') as filehandle:
			filehandle.write(content)
		return True

	def download_file(self, path):
		LOG.debug('downloading file %r', path)
		with open(path, 'r') as filehandle:
			ret = filehandle.read()
		return ret


class Executor(prove.executor.Executor):
	session_cls = Session
