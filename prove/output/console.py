import sys


def connect_start(target):
	sys.stdout.write('connecting to %s ...' % target.host)
	sys.stdout.flush()


def connect_success(target):
	sys.stdout.write(' connected!\n')
	sys.stdout.flush()


def connect_failure(target):
	sys.stdout.write(' failed!\n')
	sys.stdout.flush()


def disconnected(target):
	print('\ndisconnected from {}.'.format(target.host))


def cmd_result(result):
	print('exit code:', result.exit_code)
	if result.stderr:
		print('system stderr:')
		print(result.stderr)
	if result.stdout:
		print('system stdout:')
		print(result.stdout)


def state_fncall_start(state, state_fncall):
	sys.stdout.write('\n● {} ({})'.format(state.name, state_fncall.func))
	sys.stdout.flush()


def state_fncall_finish(state, state_fncall, result):
	print(' ✓ success' if result.success else ' ✗ failure')
	if result.changes:
		if isinstance(result.changes, str):
			result.changes = [l for l in result.changes.split('\n') if l]
		if len(result.changes) > 1:
			print('changes:\n  ' + '\n  '.join(result.changes))
		else:
			print('changes:', result.changes[0])
	comment = result.format_comment()
	if comment:
		print(comment)


def state_summary():
	pass


def comment(string):
	print(string)
