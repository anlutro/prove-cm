import socket
import subprocess

import prove.executor


class Connection(prove.executor.Connection):
	def connect(self):
		pass

	def disconnect(self):
		pass

	def run_command(self, command):
		if not isinstance(command, list):
			command = command.split()
		if len(command) == 1 and ' ' in command[0]:
			command = command[0].split()

		p = subprocess.Popen(
			command,
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
