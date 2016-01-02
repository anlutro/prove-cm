import mako.template
from prove.loaders.yaml import _ordered_load


def supports(filename):
	return filename.endswith('.yml.mako') or filename.endswith('.yaml.mako')


def load(path, variables=None):
	if variables is None:
		variables = {}

	with open(path, 'r') as f:
		template = mako.template.Template(f.read(), strict_undefined=True)

	yaml_str = template.render(**variables)

	return _ordered_load(yaml_str)
