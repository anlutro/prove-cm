from prove.state import StateResult


class SysvError(Exception):
	pass


def _is_service_running(connection, service):
	result = connection.run_command('service {} status'.format(service))
	if result.exit_code == 3:
		return False
	elif result.exit_code == 0:
		return True
	raise SysvError('Unknown exit code: {}'.format(result.exit_code))


def _start_service(connection, service):
	return connection.run_command('service {} start'.format(service))


def _is_service_enabled(connection, service):
	result = connection.run_command('chkconfig {}'.format(service))
	if result.exit_code == 127:
		log.warning('Could not determine if service is enabled because chkconfig'
			' is not installed or is not in $PATH.')
		return False
	if result.stdout.endswith('on'):
		return True
	elif result.stdout.endswith('off'):
		return False
	raise SysvError('Could not parse chkconfig stdout')


def _enable_service(connection, service):
	result = connection.run_command('chkconfig {} on'.format(service))
	if result.exit_code == 127:
		log.warning('Could not determine if service is enabled because chkconfig'
			' is not installed or is not in $PATH.')
	return result


def running(connection, args):
	result = StateResult()

	if _is_service_running(connection, args['service']):
		result.success = True
		result.comment = 'Service {} is already running'.format(args['service'])
		return result

	cmd_result = _start_service(connection, args['service'])
	if cmd_result.was_successful:
		result.success = True
		result.comment = 'Service {} was started'.format(args['service'])
		return result

	result.success = False
	result.comment = 'Service {} could not be started'.format(args['service'])
	if cmd_result.stderr:
		result.comment += '\n' + cmd_result.stderr
	if cmd_result.stdout:
		result.comment += '\n' + cmd_result.stdout
	return result


def enabled(connection, args):
	result = StateResult()

	if _is_service_enabled(connection, args['service']):
		result.success = True
		result.comment = 'Service {} is already enabled'.format(args['service'])
		return result

	cmd_result = _enable_service(connection, args['service'])
	if cmd_result.was_successful:
		result.success = True
		result.comment = 'Service {} was enableed'.format(args['service'])
		return result

	result.success = False
	result.comment = 'Service {} could not be enableed'.format(args['service'])
	if cmd_result.stderr:
		result.comment += '\n' + cmd_result.stderr
	if cmd_result.stdout:
		result.comment += '\n' + cmd_result.stdout
	return result
