import logging
import importlib
import socketserver
import traceback

from prove.config import Target
from prove.environment import TargetEnvironment
import prove.remote
import prove.executor.local
import prove.actions
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

		action_mod = importlib.import_module('prove.actions.' + data['action'])
		action_cls = prove.util.snake_to_camel_case(data['action'])
		action_cls = getattr(action_mod, action_cls + 'Action')
		action = action_cls(session, data.get('args', {}))
		action.run()

	def _send(self, status, data=None):
		response = prove.remote.encode({
			'status': status,
			'data': data,
		})
		LOG.debug('sending response: %r', response)
		self.request.sendall(response)


def run_server(bind_addr, bind_port=prove.remote.DEFAULT_PORT):
	socketserver.TCPServer.allow_reuse_address = True
	server = socketserver.TCPServer((bind_addr, bind_port), RequestHandler)

	try:
		LOG.info('listening on %s:%s', bind_addr, bind_port)
		server.serve_forever()
	finally:
		LOG.debug('closing server')
		server.server_close()
