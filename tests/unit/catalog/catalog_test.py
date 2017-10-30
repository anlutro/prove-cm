from prove.catalog import Catalog, TargetCatalog
import prove.config


def make_catalog(options=None):
	if options is None:
		options = {}
	options = prove.config.Options(options)
	roles = {}
	variables = {}
	variable_files = {}
	state_files = {}
	files = {}
	return Catalog(options=options, roles=roles, variables=variables,
		variable_files=variable_files, state_files=state_files, files=files)


def test_make_target_catalog():
	catalog = make_catalog()
	target_config = prove.config.Target('localhost')
	target_catalog = catalog.make_target_catalog(target_config)
	assert isinstance(target_catalog, TargetCatalog)
