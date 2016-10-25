from prove.states import StateResult


def run(session, args):
	assert 'command' in args, 'Must provide "command" argument'
	result = session.run_command(args.get('command'))

	return StateResult(
		success=result.was_successful,
		changes=None,
		stdout=result.stdout,
		stderr=result.stderr,
	)
