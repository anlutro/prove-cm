import logging
import ssl
import socketserver
import traceback

from prove.config import Target
from prove.environment import TargetEnvironment
import prove.remote
import prove.executor.local
import prove.output.composite
import prove.output.log
import prove.output.remote

LOG = logging.getLogger(__name__)


class RequestHandler(socketserver.BaseRequestHandler):
	def handle(self):
		LOG.debug('starting request handler')
		self._send('starting')
		try:
			self._handle()
			LOG.debug('successfully finished handling request')
		except Exception as e:
			self._send('error', traceback.format_exc())
			raise
		finally:
			self._send('finished')

	def _handle(self):
		payload = prove.remote.read_socket(self.request)
		LOG.debug('received: %r', payload)
		data = prove.remote.decode(payload)

		target = prove.remote.unserialize(data['target'])
		assert isinstance(target, Target)

		env = prove.remote.unserialize(data['env'])
		assert isinstance(env, TargetEnvironment)

		output = prove.output.composite.CompositeOutput(
			prove.output.log,
			prove.output.remote.RemoteOutput(self._send)
		)

		session = prove.executor.local.Session(target, env, output)

		action_cls = prove.operations.get_action_cls(data['action'])
		action = action_cls(session, data.get('args', {}))
		action.run()

	def _send(self, status, data=None):
		response = prove.remote.encode({
			'status': status,
			'data': data,
		})
		LOG.debug('sending response: %r', response)
		self.request.sendall(response)


class RemoteServer(socketserver.TCPServer):
	def __init__(self, *args, cafile, certfile, keyfile, **kwargs):
		super().__init__(*args, **kwargs)
		self.certfile = certfile
		self.keyfile = keyfile
		self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
		self.ssl_context.verify_mode = ssl.CERT_REQUIRED
		LOG.info('loading ssl ca: %r', cafile)
		self.ssl_context.load_verify_locations(cafile=cafile)
		LOG.info('loading ssl cert: %r', certfile)
		LOG.info('loading ssl key: %r', keyfile)
		self.ssl_context.load_cert_chain(certfile, keyfile)

	def get_request(self):
		sock, fromaddr = self.socket.accept()
		try:
			sock = self.ssl_context.wrap_socket(
				sock,
				server_side=True,
			)
		except:
			LOG.exception('uncaught exception in ssl.wrap_socket')
			raise
		return sock, fromaddr


class ThreadedRemoteServer(socketserver.ThreadingMixIn, RemoteServer):
	pass


def run_server(bind_addr, bind_port, ca_path, ssl_cert, ssl_key):
	socketserver.TCPServer.allow_reuse_address = True
	server = RemoteServer(
		(bind_addr, bind_port),
		RequestHandler,
		cafile=ca_path,
		certfile=ssl_cert,
		keyfile=ssl_key,
	)

	try:
		LOG.info('listening on %s:%s', bind_addr, bind_port)
		server.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		LOG.debug('closing server')
		server.server_close()
