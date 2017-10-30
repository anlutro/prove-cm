from prove.catalog.states import StateFuncResult


class TimezoneState():
	def __init__(self, session):
		self.session = session

	def _timedatectl(self):
		data = {}
		for line in self.session.run_command('timedatectl').stdout.splitlines():
			if ': ' in line:
				key, val = line.split(': ', 1)
				key = key.strip()
				data[key] = val.strip()
			else:
				data[key] += ' ' + line.strip()
		return data

	def _get_tz(self):
		timedata = self._timedatectl()
		timezonedata = timedata['Time zone']
		return timezonedata.split()[0]

	def _set_tz(self, timezone):
		return True

	def set_timezone(self, timezone):
		result = StateFuncResult(success=True)
		old_tz = self._get_tz()
		if old_tz == timezone:
			result.comment = 'timezone already set to %s' % old_tz
		else:
			result.success = self._set_tz(timezone)
			if result.success:
				result.changes = 'timezone changed from %s to %s' % (old_tz, timezone)
		return result


def set(session, args):
	return TimezoneState(session).set_timezone(**args)
