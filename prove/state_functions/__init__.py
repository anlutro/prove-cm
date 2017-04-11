from prove.states import StateResult


class AbstractState:
	def __init__(self, session):
		self.session = session

	def run_command(self, command, skip_sudo=False):
		return self.session.run_command(command, skip_sudo=skip_sudo)

	def result(self, *args, **kwargs):
		return StateResult(*args, **kwargs)
