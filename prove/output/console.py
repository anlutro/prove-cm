import sys


def connect_start(target):
	sys.stdout.write('Connecting to {}...'.format(target.host))
	sys.stdout.flush()


def connect_success(target):
	sys.stdout.write(' Connected!\n')
	sys.stdout.flush()


def connect_failure(target):
	sys.stdout.write(' Failed!\n')
	sys.stdout.flush()


def disconnected(target):
	pass


def cmd_result(result):
	print('Exit code:', result.exit_code)
	if result.stderr:
		print('STDERR:')
		print(result.stderr)
	if result.stdout:
		print('STDOUT:')
		print(result.stdout)


def state_invocation_start(state, state_invocation):
	print('=> {} -- {}'.format(state.name, state_invocation.func))


def state_invocation_finish(state, state_invocation, result):
	print('Result: ', 'success' if result.success else 'failure')
	if result.changes:
		print('Changes:', '\n         '.join(result.changes))
	else:
		print('Changes: None')
	if result.comment:
		print(result.comment)


def state_summary():
	pass
