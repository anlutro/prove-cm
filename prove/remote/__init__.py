import base64
import json
import pickle
import logging

LOG = logging.getLogger(__name__)
DEFAULT_PORT = 9999
LINE_DELIMITER = b'\0'


def read_socket(socket, buf_size=4096):
	LOG.debug('waiting for socket.recv')

	payload = socket.recv(buf_size)
	while payload and not payload.endswith(LINE_DELIMITER):
		LOG.debug('socket.recv incomplete, waiting for more')
		add_payload = socket.recv(buf_size)
		if add_payload == b'':
			raise ValueError('received empty binary data')
		payload += add_payload

	LOG.debug('finished socket.recv')
	return payload


def encode(data):
	assert isinstance(data, dict)
	return json.dumps(data).encode('ascii') + LINE_DELIMITER


def decode(payload):
	string = payload.rstrip(LINE_DELIMITER).decode('ascii')
	return json.loads(string)


def serialize(obj):
	# base64 encode the pickle data so that it can be embedded in json
	return 'pickle::' + base64.b64encode(pickle.dumps(obj)).decode('ascii')


def unserialize(string):
	if string.startswith('pickle::'):
		return pickle.loads(base64.b64decode(string[8:]))

	if len(string) > 16:
		string = '{}...'.format(string[:16])
	raise RuntimeError("don't know how to unserialize %r" % string)
