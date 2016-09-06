import base64
import json
import pickle
import logging
import importlib

LOG = logging.getLogger(__name__)
DEFAULT_PORT = 9999
LINE_DELIMITER = b'\0'


def run_server(config):
	options = config.get('options', {})
	server_mod = importlib.import_module(
		'prove.remote.transport.%s.server' % options['remote_transport']
	)
	ssl_conf = options.get('ssl', {})
	server_mod.run_server(
		options['agent']['bind'],
		options['agent']['port'],
		ca_path=ssl_conf['ca_path'],
		ssl_cert=ssl_conf['agent_cert'],
		ssl_key=ssl_conf['agent_key'],
	)


def get_client(target, env, callback):
	client_mod = importlib.import_module(
		'prove.remote.transport.%s.client' % env.options['remote_transport']
	)
	return client_mod.get_client(target, env, callback)


def read_socket(sock, buf_size=4096):
	LOG.debug('waiting for socket.recv')

	payload = sock.recv(buf_size)
	while payload and not payload.endswith(LINE_DELIMITER):
		LOG.debug('socket.recv incomplete, waiting for more')
		add_payload = sock.recv(buf_size)
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
