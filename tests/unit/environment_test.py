from prove.environment import Environment, TargetEnvironment
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


def test_make_target_env():
	env = make_env()
	target_config = prove.config.Target('localhost')
	target_env = env.make_target_env(target_config)
	assert isinstance(target_env, TargetEnvironment)
