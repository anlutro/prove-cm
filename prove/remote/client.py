import logging
import socket
import ssl

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
		self.socket.send(prove.remote.encode(data))
		response = {'status': 'initiating'}

		try:
			while response['status'] != 'finished':
				LOG.debug('status %r != finished, waiting for more data',
					response['status'])
				responses = self._receive()
				for response in responses:
					self.callback(response)
		finally:
			self.disconnect()

	def _receive(self):
		data = prove.remote.read_socket(self.socket)
		if data == b'':
			raise ValueError('received empty binary response')

		responses = []

		for line in data.split(prove.remote.LINE_DELIMITER):
			if line:
				responses.append(prove.remote.decode(line))

		return responses

	def disconnect(self):
		self.socket.close()


class RemoteSocket:
	def __init__(self, host, port, cafile=None, certfile=None, keyfile=None, keypass=None):
		self.host = host
		self.port = port
		self.socket = None

		if cafile or certfile:
			self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
			# alternatively: https://docs.python.org/3/library/ssl.html#protocol-versions
			# self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSL_v23)
			# self.ssl_context.options |= ssl.OP_NO_SSLv2 # pylint: disable=no-member
			# self.ssl_context.options |= ssl.OP_NO_SSLv3 # pylint: disable=no-member

			self.ssl_context.verify_mode = ssl.CERT_REQUIRED
			self.ssl_context.check_hostname = True
			if cafile:
				LOG.info('loading ssl ca: %r', cafile)
				self.ssl_context.load_verify_locations(cafile=cafile)
			if certfile:
				LOG.info('loading ssl cert: %r', certfile)
				LOG.info('loading ssl key: %r - password: %s',
					keyfile, 'yes' if keypass else 'no')
				self.ssl_context.load_cert_chain(certfile, keyfile, keypass)
		else:
			self.ssl_context = None

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
				if self.ssl_context:
					self.socket = self.ssl_context.wrap_socket(
						self.socket, server_hostname=self.host
					)
			except ConnectionRefusedError:
				LOG.debug('connection refused: %s:%s', address[0], address[1], exc_info=True)
				self.close()
				continue

			try:
				self.socket.settimeout(10)
				LOG.debug('Trying to connect to %s:%s', address[0], address[1])
				self.socket.connect(address)
			except ConnectionRefusedError:
				LOG.debug('connection refused: %s:%s', address[0], address[1], exc_info=True)
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
		LOG.debug('sending data: %r', data)
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
			LOG.debug("OSError on socket.shutdown, but we think it's ok",
				exc_info=True)
			pass

		self.socket.close()
		self.socket = None
