import argparse

import prove.client
import prove.remote
import prove.remote.server


class AgentDaemon(prove.client.AbstractClient):
	def __init__(self, args=None):
		parser = argparse.ArgumentParser(description="Prove - a configuration manager")
		parser.add_argument('-c', '--config',
			help="Path to config file")
		parser.add_argument('-l', '--log-level',
			help="Set the log level")
		parser.add_argument('--log-path',
			help="Set the log path")
		parser.add_argument('-b', '--bind', default='localhost',
			help="Address to bind to")
		parser.add_argument('-p', '--port', default=prove.remote.DEFAULT_PORT,
			help="Port to listen on")
		super().__init__(parser.parse_args(args))

	def main(self):
		config = self.read_config()
		ssl_opts = config.get('options', {}).get('ssl', {})
		prove.remote.server.run_server(
			self.args.bind,
			self.args.port,
			ca_path=ssl_opts['ca_path'],
			ssl_cert=ssl_opts['agent_cert'],
			ssl_key=ssl_opts['agent_key'],
		)


def main():
	AgentDaemon().main()


if __name__ == '__main__':
	main()
