from prove.states import StateResult
from prove.state_functions import AbstractState


def _locale_variations(locale):
	variations = set()
	variations.add(locale)
	variations.add(locale.replace('UTF-8', 'utf8'))
	variations.add(locale.replace('utf8', 'UTF-8'))
	return variations


def _full_locale(locale):
	parts = locale.split()
	if len(parts) == 1 and '.' in locale:
		parts = locale.split('.')
		locale = '%s.%s %s' % (parts[0], parts[1], parts[1])
	return locale


class LocaleState(AbstractState):
	def install_locale(self, locale):
		result = StateResult(success=True)
		localegen_path = '/etc/locale.gen'

		for variation in _locale_variations(locale):
			search_result = self.run_command('locale -a | grep -P "^%s"' % variation.replace('.', '\.'))
			if search_result.was_successful:
				result.comment = 'locale already present'
				return result

		result.changes = []

		locale_exists_in_localegen = False
		for variation in _locale_variations(locale):
			search_result = self.run_command('grep -P "^%s" %s' % (variation.replace('.', '\.'), localegen_path))
			if search_result.was_successful:
				locale_exists_in_localegen = True
				locale = variation
				break

		if not locale_exists_in_localegen:
			commented_locale_exists = False

			for variation in _locale_variations(locale):
				search_result = self.run_command('grep -P "^#\s*%s" %s' % (variation.replace('.', '\.'), localegen_path))
				if search_result.was_successful:
					commented_locale_exists = True
					locale = variation
					break

			if commented_locale_exists:
				sed_cmd = 'sed -r -i.bak "s/^#\s*(%s.*)/\1/" %s' % (locale.replace('.', '\.'), localegen_path)
				sed_result = self.run_command(sed_cmd)
				if not sed_result.was_successful:
					result.success = False
					result.stderr = sed_result.stderr
					return result
				result.changes.append('uncommented locale %r from %s' % (locale, localegen_path))
			else:
				self.run_command('echo "%s" >> %s' % (_full_locale(locale), localegen_path))
				result.changes.append('added locale %r to %s' % (locale, localegen_path))

		localegen_result = self.run_command('locale-gen')
		result.merge_with_cmd_result(localegen_result)

		return result


def present(session, args):
	return LocaleState(session).install_locale(**args)


def set_system(session, args):
	return LocaleState(session).set_locale(**args)
