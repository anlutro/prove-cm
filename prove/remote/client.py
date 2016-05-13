import base64
import json
import logging
import pickle
import socket

LOG = logging.getLogger(__name__)


class RemoteClientException(Exception):
	pass


def pickle_jsonsafe(obj):
	pickle_value = pickle.dumps(obj)
	bytes_value = base64.b64encode(pickle_value)
	return bytes_value.decode('ascii')


class RemoteClient:
	def __init__(self, sock, callback, host, env):
		self.socket = sock
		self.callback = callback
		self.host = host
		self.env = env

	def connect(self):
		self.socket.connect()

	def run_action(self, action):
		data = {
			'host_pickle': pickle_jsonsafe(self.host),
			'env_pickle': pickle_jsonsafe(self.env),
			'action': action.name,
			'args': action.args,
		}
		self.socket.send(json.dumps(data))

		try:
			data = self.socket.recv()
			self.callback(data)
			while data != b'\x00':
				data = self.socket.recv()
				self.callback(data)
		finally:
			self.disconnect()

	def disconnect(self):
		self.socket.close()


class RemoteSocket:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = None

	def connect(self):
		LOG.debug('Looking up address info for %s:%s', self.host, self.port)
		addrinfo = socket.getaddrinfo(
			self.host, self.port,
			socket.AF_UNSPEC, socket.SOCK_STREAM
		)

		for res in addrinfo:
			af, socktype, proto, canonname, address = res

			try:
				self.socket = socket.socket(af, socktype, proto)
			except OSError:
				self.socket = None
				continue

			try:
				self.socket.settimeout(10)
				LOG.debug('Trying to connect to %s:%s', address[0], address[1])
				self.socket.connect(address)
			except OSError:
				self.close()
				continue

			# if we reach this point, the socket has been successfully created,
			# so break out of the loop
			break

		if self.socket is None:
			raise RemoteClientException('Could not connect to {}:{}'.format(
				self.host, self.port))

		self.socket.settimeout(None)

	def recv(self, bufsize=4096):
		return self.socket.recv(bufsize)

	def send(self, data):
		if isinstance(data, str):
			data = data.encode('utf-8')
		return self.socket.send(data)

	def close(self):
		# socket may already have been closed
		if not self.socket:
			return

		try:
			self.socket.shutdown(socket.SHUT_RDWR)
		except OSError:
			# shutdown will fail if the socket has already been closed by the
			# server, which will happen if we get throttled for example
			pass
		self.socket.close()
		self.socket = None
