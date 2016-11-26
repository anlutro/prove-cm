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
	print('\nDisconnected from {}.'.format(target.host))


def cmd_result(result):
	print('Exit code:', result.exit_code)
	if result.stderr:
		print('STDERR:')
		print(result.stderr)
	if result.stdout:
		print('STDOUT:')
		print(result.stdout)


def state_funcall_start(state, state_funcall):
	sys.stdout.write('\n=> {} -- {}'.format(state.name, state_funcall.func))
	sys.stdout.flush()


def state_funcall_finish(state, state_funcall, result):
	print(' --', 'success' if result.success else 'failure')
	if result.changes:
		if len(result.changes) > 1:
			print('Changes:\n  ', '\n  '.join(result.changes))
		else:
			print('Changes:', result.changes[0])
	comment = result.format_comment()
	if comment:
		print(comment)


def state_summary():
	pass


def comment(string):
	print(string)
