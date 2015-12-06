import yaml


def supports(filename):
	return filename.endswith('.yml') or filename.endswith('.yaml')


def load(path, variables):
	with open(path, 'r') as f:
		return yaml.load(f)
