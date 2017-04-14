from prove.states import StateFuncResult


def run(session, args):
	result = session.run_command(args['command'])

	return StateFuncResult(
		success=result.was_successful,
		changes=None,
		stdout=result.stdout,
		stderr=result.stderr,
	)
