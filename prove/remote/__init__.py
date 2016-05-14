import base64
import pickle

DEFAULT_PORT = 9999


def serialize(object):
	pickle_value = pickle.dumps(object)
	bytes_value = base64.b64encode(pickle_value)
	return bytes_value.decode('ascii')


def unserialize(string):
	bytes_value = string.encode('ascii')
	pickle_value = base64.b64decode(bytes_value)
	return pickle.loads(pickle_value)
