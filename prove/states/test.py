from prove.state import StateResult


def succeed_without_changes(session, args):
	return StateResult(success=True)


def succeed_with_changes(session, args):
	return StateResult(success=True, changes=['changes'])


def fail_without_changes(session, args):
	return StateResult(success=False)


def fail_with_changes(session, args):
	return StateResult(success=False, changes=['changes'])
