import sys


def connect_start(host):
	sys.stdout.write('Connecting to {}...'.format(host.host))
	sys.stdout.flush()


def connect_success(host):
	sys.stdout.write(' Connected!\n')
	sys.stdout.flush()


def connect_failure(host):
	sys.stdout.write(' Failed!\n')
	sys.stdout.flush()


def disconnected(host):
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
	print('=> {} -- {}'.format(state.name, state_invocation.fn))


def state_invocation_finish(state, state_invocation, result):
	print('Result: ', 'success' if result.success else 'failure')
	print('Changes:', result.changes)
	if result.comment:
		print(result.comment)


def state_summary():
	pass
