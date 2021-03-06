import copy
import mako.template
from prove.loaders import LoaderException
from prove.loaders.yaml import _ordered_load


class Variables(dict):
	def __getattr__(self, key):
		val = self[key]
		if isinstance(val, dict):
			self[key] = Variables(val)
			val = self[key]
		return val


def supports(filename):
	return filename.endswith('.yml.mako') or filename.endswith('.yaml.mako')


def load(path, variables=None):
	if variables is None:
		variables = {}
	else:
		variables = copy.deepcopy(variables)

	try:
		with open(path, 'r') as file:
			template = mako.template.Template(file.read(), strict_undefined=True)
		yaml_str = template.render(vars=Variables(variables))
	except Exception as e:
		raise LoaderException('error loading mako file %r' % path) from e

	return _ordered_load(yaml_str)
