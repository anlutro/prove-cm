from prove.environment import Environment, HostEnvironment
import prove.config


def make_env(options=None):
	if options is None:
		options = {}
	options = prove.config.Options(options)
	roles = {}
	variables = {}
	variable_files = {}
	state_files = {}
	files = {}
	return Environment(options=options, roles=roles, variables=variables,
		variable_files=variable_files, state_files=state_files, files=files)


def test_make_host_env():
	env = make_env()
	host_config = prove.config.HostConfig('localhost')
	host_env = env.make_host_env(host_config)
	assert isinstance(host_env, HostEnvironment)
