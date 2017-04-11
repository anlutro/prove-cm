import sys
import textwrap
import prove.util


BEFORE_STATE_CHAR = ''
BEFORE_FNCALL_CHAR = '→'
STATE_RESULT_ITEM = '·'


class tc:
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	WHITE = '\033[97m'
	GREY = '\033[0;37m'
	RESET = '\033[0m'
	BOLD = '\033[1m'


def connect_start(target):
	sys.stdout.write('connecting to %s …' % target.host)
	sys.stdout.flush()


def connect_success(target):
	print(' connected!')


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


def state_start(state):
	print()
	line = ' %s %s' % (BEFORE_STATE_CHAR, state.name)
	print('%s%s%s' % (tc.YELLOW, line.strip(), tc.RESET))


def state_fncall_start(state, fncall):
	sys.stdout.write(' ' * (3 if BEFORE_STATE_CHAR else 1))
	sys.stdout.write('%s %s(%s) …' % (BEFORE_FNCALL_CHAR, fncall.func, fncall.main_arg))
	sys.stdout.flush()


def state_fncall_finish(state, fncall, result):
	indent = 5 if BEFORE_STATE_CHAR else 3
	if result.success:
		print(' %s✓ success%s' % (tc.GREEN, tc.RESET))
	else:
		print(' %s✗ failure%s' % (tc.RED, tc.RESET))
	sys.stdout.write(tc.GREY)

	wrapper = textwrap.TextWrapper(
		initial_indent=' ' * indent + ' ' + STATE_RESULT_ITEM + ' ',
		subsequent_indent=' ' * (indent+3),
		tabsize=4,
	)

	if result.comment:
		print(wrapper.fill(result.comment))

	if result.comments:
		for comment in result.comments:
			print(wrapper.fill(comment))

	if result.changes:
		if isinstance(result.changes, str):
			result.changes = [l for l in result.changes.split('\n') if l]
		print(' ' * indent + 'changes:')
		for change in result.changes:
			print(wrapper.fill(change))

	if result.stdout:
		print(' ' * indent + 'system stdout:')
		print(prove.util.indent_string(result.stdout, indent + 2))

	if result.stderr:
		print(' ' * indent + 'system stderr:')
		print(prove.util.indent_string(result.stderr, indent + 2))

	sys.stdout.write(tc.RESET)


def state_summary():
	pass


def comment(string):
	print(string)
