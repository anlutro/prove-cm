from prove.state import StateResult


def run(session, args):
	assert 'cmd' in args, 'Must provide "cmd" argument'
	result = session.run_command(args.get('cmd'))

	comments = []
	if result.stderr:
		comments.append('STDERR:\n' + result.stderr)
	if result.stdout:
		comments.append('STDOUT:\n' + result.stdout)

	return StateResult(
		success=result.was_successful,
		changes=None,
		comment='\n'.join(comments)
	)
