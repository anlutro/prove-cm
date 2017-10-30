# pylint: disable=unused-argument

from prove.catalog.states import StateFuncResult


def succeed_without_changes(session, args):
	return StateFuncResult(success=True)


noop = succeed_without_changes


def succeed_with_changes(session, args):
	return StateFuncResult(success=True, changes=['changes'])


def fail_without_changes(session, args):
	return StateFuncResult(success=False)


def fail_with_changes(session, args):
	return StateFuncResult(success=False, changes=['changes'])


def throw_exception(session, args):
	raise RuntimeError('Test error')


def long_output(session, args):
	lipsum = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed '
		'vulputate porttitor neque nec sagittis. Duis sit amet arcu quis felis '
		'feugiat volutpat.')
	stdout = (
		'total 16K\n'
		'drwxr-xr-x 5 andreas andreas 4.0K 2016-04-29 23:24 example/\n'
		'drwxr-xr-x 5 andreas andreas 4.0K 2017-04-10 19:49 real/\n'
		'drwxr-xr-x 5 andreas andreas 4.0K 2017-04-10 20:23 test/\n'
		'drwxr-xr-x 2 andreas andreas 4.0K 2016-10-25 22:00 vagrant/\n'
	)
	stderr = (
		'W: chmod 0700 of directory /var/lib/apt/lists/partial failed - SetupAPTPartialDirectory (1: Operation not permitted)\n'
		'E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)\n'
		'E: Unable to lock directory /var/lib/apt/lists/\n'
		'W: Problem unlinking the file /var/cache/apt/pkgcache.bin - RemoveCaches (13: Permission denied)\n'
		'W: Problem unlinking the file /var/cache/apt/srcpkgcache.bin - RemoveCaches (13: Permission denied)\n'
	)
	return StateFuncResult(
		success=False,
		changes=[lipsum, lipsum],
		comments=[lipsum, lipsum],
		stdout=stdout,
		stderr=stderr,
	)
