import json
import logging
import socket

import prove.remote

LOG = logging.getLogger(__name__)


class RemoteClientException(Exception):
	pass


class RemoteClient:
	def __init__(self, sock, callback, target, env):
		self.socket = sock
		self.callback = callback
		self.target = target
		self.env = env

	def connect(self):
		self.socket.connect()

	def run_action(self, action):
		data = {
			'action': action.name,
			'args': action.args,
			'env': prove.remote.serialize(self.env),
			'target': prove.remote.serialize(self.target),
		}
		self.socket.send(json.dumps(data))
		response = {'status': None}

		try:
			while response['status'] != 'finished':
				responses = self._receive()
				for response in responses:
					self.callback(response)
		finally:
			self.disconnect()

	def _receive(self):
		data = self.socket.recv(4196).decode('ascii')
		while data[-1] != '\n':
			data += self.socket.recv(4196).decode('ascii')

		responses = []

		for line in data.split('\n'):
			if line:
				responses.append(json.loads(line))

		return responses

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
