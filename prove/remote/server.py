import json
import logging
import importlib
import socketserver

from prove.config import Target
from prove.environment import TargetEnvironment
import prove.remote
import prove.executor.local
import prove.actions
import prove.output.composite
import prove.output.log
import prove.output.remote

LOG = logging.getLogger(__name__)


def run_server(bind_addr, bind_port=prove.remote.DEFAULT_PORT):
	class RequestHandler(socketserver.BaseRequestHandler):
		def handle(self):
			LOG.debug('Handling request')
			self._send('starting')
			try:
				target, env, action = self._read()
				output = prove.output.composite.CompositeOutput(
					prove.output.log,
					prove.output.remote.RemoteOutput(self._send)
				)
				session = prove.executor.local.Session(target, env, output)
				action.run(session)
				LOG.debug('Finished handling request')
			finally:
				self._send('finished')

		def _send(self, status, data=None):
			json_data = json.dumps({
				'status': status,
				'data': data,
			})
			LOG.debug(json_data)
			self.request.sendall((json_data + '\n').encode('ascii'))

		def _read(self):
			payload = self.request.recv(4096).decode('ASCII').strip()
			data = json.loads(payload)

			target = prove.remote.unserialize(data['target'])
			assert isinstance(target, Target)

			env = prove.remote.unserialize(data['env'])
			assert isinstance(env, TargetEnvironment)

			action_mod = importlib.import_module('prove.actions.' + data['action'])
			action_class = prove.util.snake_to_camel_case(data['action'])
			action_class = getattr(action_mod, action_class + 'Action')
			action = action_class(data.get('args', {}))

			return target, env, action

	socketserver.TCPServer.allow_reuse_address = True
	server = socketserver.TCPServer((bind_addr, bind_port), RequestHandler)

	try:
		LOG.debug('Listening on %s:%s', bind_addr, bind_port)
		server.serve_forever()
	finally:
		LOG.debug('Closing server')
		server.server_close()


def main():
	run_server('0.0.0.0')

if __name__ == '__main__':
	main()
