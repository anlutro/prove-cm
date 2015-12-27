from prove.state.command import _run_command

def lazy_load(client):
	result = _run_command(client, 'lsb_release -a')

	if 'Debian GNU/Linux' in result.stdout:
		import prove.states.pkg.apt
		return prove.states.pkg.apt

	raise Exception("Could not find appropriate pkg module for OS")
