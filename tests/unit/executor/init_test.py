from prove.executor import command_with_sudo, parse_lsb_release


def test_run_command_sudo():
	assert "sudo -n -- sh -c ls" == command_with_sudo('ls')
	assert "sudo -n -- sh -c 'echo foo; echo bar'" == command_with_sudo('echo foo; echo bar')
	assert "sudo -n -- sh -c 'echo \"foo bar\"'" == command_with_sudo('echo "foo bar"')
	assert "sudo -n -- sh -c 'echo foo | grep foo'" == command_with_sudo('echo foo | grep foo')


def test_parse_lsb_release():
	output = (
		'No LSB modules are available.\n'
		'Distributor ID:	Debian\n'
		'Description:	Debian GNU/Linux 8.7 (jessie)\n'
		'Release:	8.7\n'
		'Codename:	jessie\n'
	)
	data = parse_lsb_release(output)
	assert data['Distributor ID'] == 'Debian'
	assert data['Release'] == '8.7'
	assert data['Codename'] == 'jessie'
