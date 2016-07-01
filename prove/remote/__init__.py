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
	# 0 == b'\0'
	while payload and payload[-1] != 0:
		LOG.debug('socket.recv incomplete, waiting for more')
		payload += socket.recv(buf_size)

	LOG.debug('finished socket.recv')
	return payload


def encode(data):
	assert isinstance(data, dict)
	return json.dumps(data).encode('ascii') + LINE_DELIMITER


def decode(payload):
	string = payload.rstrip(LINE_DELIMITER).decode('ascii')
	print(string)
	return json.loads(string)


def serialize(obj):
	# base64 encode the pickle data so that it can be embedded in json
	return base64.b64encode(pickle.dumps(obj)).decode('ascii')


def unserialize(string):
	return pickle.loads(base64.b64decode(string))
