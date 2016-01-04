import json


def supports(filename):
	return filename.endswith('.json')


def load(path, variables=None):
	with open(path, 'r') as file:
		return json.load(file)
