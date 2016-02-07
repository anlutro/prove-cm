import base64
import json
import logging
import importlib
import pickle
import socketserver

from prove.config import HostConfig
from prove.environment import HostEnvironment
import prove.remote
import prove.executor.local
import prove.actions
import prove.output.log

log = logging.getLogger(__name__)


def unpickle_jsonsafe(string):
	bytes_value = string.encode('ascii')
	pickle_value = base64.b64decode(bytes_value)
	return pickle.loads(pickle_value)


def run_server(bind_addr, bind_port=prove.remote.DEFAULT_PORT):
	class RequestHandler(socketserver.BaseRequestHandler):
		def handle(self):
			log.debug('Handling request')
			self.request.sendall(b'STARTING')
			host, env, action = self._read()
			output = prove.output.log
			session = prove.executor.local.Session(host, env, output)
			action.run(session)
			log.debug('Finished handling request')
			self.request.sendall(b'\x00')

		def _read(self):
			payload = self.request.recv(4096).decode('ASCII').strip()
			data = json.loads(payload)

			host = unpickle_jsonsafe(data['host_pickle'])
			assert isinstance(host, HostConfig)

			env = unpickle_jsonsafe(data['env_pickle'])
			assert isinstance(env, HostEnvironment)

			action_mod = importlib.import_module('prove.actions.' + data['action'])
			action_class = prove.util.snake_to_camel_case(data['action'])
			action_class = getattr(action_mod, action_class + 'Action')
			action = action_class(data.get('args', {}))

			return host, env, action

	socketserver.TCPServer.allow_reuse_address = True
	server = socketserver.TCPServer((bind_addr, bind_port), RequestHandler)

	try:
		log.debug('Listening on %s:%s', bind_addr, bind_port)
		server.serve_forever()
	finally:
		log.debug('Closing server')
		server.server_close()


def main():
	run_server('0.0.0.0')

if __name__ == '__main__':
	main()
