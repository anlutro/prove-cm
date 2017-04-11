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
	extra = prove.util.format_result(stdout=result.stdout, stderr=result.stderr)
	if extra:
		logstr += extra
	LOG.info(logstr)


def state_fncall_start(state, state_fncall):
	LOG.info('Starting state function call: %s -- %s',
		state.name, state_fncall.func)


def state_fncall_finish(state, state_fncall, result):
	logstr = 'State function call finished: '
	logstr += 'success' if result.success else 'failure'
	if result.changes:
		logstr += '\n'
		logstr += '\n  '.join(result.changes)
	comment = result.format_comment()
	if comment:
		logstr += '\n' + comment
	LOG.info(logstr)


def state_summary():
	pass


def remote_error(error_string, target):
	LOG.error('remote target "%s" had an uncaught error:\n%s',
		target.name, error_string.strip())


def comment(string):
	LOG.info(string)
