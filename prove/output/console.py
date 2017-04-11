import sys
import prove.util


class tc:
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	RESET = '\033[0m'
	BOLD = '\033[1m'


def connect_start(target):
	sys.stdout.write('connecting to %s ...' % target.host)
	sys.stdout.flush()


def connect_success(target):
	sys.stdout.write(' connected!\n')
	sys.stdout.flush()


def connect_failure(target):
	sys.stdout.write(' %s✗ failed!%s\n' % (tc.RED, tc.RESET))
	sys.stdout.flush()


def disconnected(target):
	print('\ndisconnected from {}.'.format(target.host))


def cmd_result(result):
	icon = ('%s✓ ' % tc.GREEN) if result.exit_code == 0 else ('%s✗ ' % tc.RED)
	print('exit code: ' + icon + str(result.exit_code) + tc.RESET)
	comment = prove.util.format_result(stdout=result.stdout, stderr=result.stderr)
	if comment:
		print(comment)


def state_fncall_start(state, state_fncall):
	sys.stdout.write('\n● {} ({})'.format(state.name, state_fncall.func))
	sys.stdout.flush()


def state_fncall_finish(state, state_fncall, result):
	if result.success:
		print(' %s✓ success%s' % (tc.GREEN, tc.RESET))
	else:
		print(' %s✗ failure%s' % (tc.RED, tc.RESET))
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
