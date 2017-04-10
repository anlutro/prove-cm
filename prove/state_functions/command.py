from prove.states import StateResult


def run(session, args):
	result = session.run_command(args['command'])

	return StateResult(
		success=result.was_successful,
		changes=None,
		stdout=result.stdout,
		stderr=result.stderr,
	)
