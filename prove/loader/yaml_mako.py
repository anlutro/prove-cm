import yaml
import mako.template
import prove.utils


def supports(filename):
	return filename.endswith('.yml.mako') or filename.endswith('.yaml.mako')


def load(path, variables):
	with open(path, 'r') as f:
		yaml_str = mako.template.Template(f.read()).render(**variables)
	return yaml.load(yaml_str, prove.utils.CustomYAMLLoader)
