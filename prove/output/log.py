import logging

LOG = logging.getLogger('prove.output')


def connect_start(target):
	LOG.info('Connecting to %s...', target.host)


def connect_success(target):
	LOG.info('Connected to %s!', target.host)


def connect_failure(target):
	LOG.info('Failed to connect to %s!', target.host)


def disconnected(target):
	LOG.info('Disconnected from %s', target.host)


def cmd_result(result):
	logstr = 'Command finished - exit code: {}'.format(result.exit_code)
	if result.stderr:
		logstr += '\nSTDERR:\n{}'.format(result.stderr)
	if result.stdout:
		logstr += '\nSTDOUT:\n{}'.format(result.stdout)
	LOG.info(logstr)


def state_invocation_start(state, state_invocation):
	LOG.info('Starting state invocation: %s -- %s',
		state.name, state_invocation.func)


def state_invocation_finish(state, state_invocation, result):
	logstr = 'State invocation finished: '
	logstr += 'success' if result.success else 'failure'
	if result.changes:
		logstr += '\n'
		logstr += '\n  '.join(result.changes)
	if result.comment:
		logstr += '\n' + result.comment
	LOG.info(logstr)


def state_summary():
	pass


def error(error_string):
	LOG.error(error_string)
