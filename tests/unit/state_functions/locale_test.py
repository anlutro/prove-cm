from prove.state_functions.locale import _full_locale, _locale_variations


def test_locale_variations():
	variations = {'en_US.UTF-8', 'en_US.utf8'}
	assert variations == _locale_variations('en_US.UTF-8')
	assert variations == _locale_variations('en_US.utf8')


def test_full_locale():
	assert 'C' == _full_locale('C')
	assert 'en_US.UTF-8 UTF-8' == _full_locale('en_US.UTF-8')
