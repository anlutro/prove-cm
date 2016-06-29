from prove.states import StateResult


def succeed_without_changes(session, args):
	return StateResult(success=True)


noop = succeed_without_changes


def succeed_with_changes(session, args):
	return StateResult(success=True, changes=['changes'])


def fail_without_changes(session, args):
	return StateResult(success=False)


def fail_with_changes(session, args):
	return StateResult(success=False, changes=['changes'])


def throw_exception(session, args):
	raise RuntimeError('Test error')
