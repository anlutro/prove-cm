from prove.state import StateResult


class SystemdError(Exception):
	pass


def _is_service_running(connection, service):
	result = connection.run_command('systemctl show {}'.format(service))
	if 'ActiveState=active' in result.stdout:
		is_running = True
	elif 'ActiveState=inactive' in result.stdout:
		is_running = False
	else:
		raise Exception('Could not parse systemctl show')
	return is_running


def _start_service(connection, service):
	return connection.run_command('systemctl start {}'.format(service))


def _is_service_enabled(connection, service):
	result = connection.run_command('systemctl is-enabled {}'.format(service))
	if result.exit_code == 0:
		return True
	elif result.exit_code == 1:
		return False
	else:
		raise SystemdError(result.stderr or result.stdout)


def _enable_service(connection, service):
	return connection.run_command('systemctl enable {}'.format(service))


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