import argparse

import prove.cli
import prove.remote


class AgentDaemon(prove.cli.AbstractClient):
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
		parser.add_argument('-p', '--port', type=int, default=prove.remote.DEFAULT_PORT,
			help="Port to listen on")
		super().__init__(parser.parse_args(args))

	def get_config(self):
		config = super().get_config()

		if 'agent' not in config['options']:
			config['options']['agent'] = {}

		if self.args.bind:
			config['options']['agent']['bind'] = self.args.bind

		if self.args.port:
			config['options']['agent']['port'] = self.args.port

		return config

	def main(self):
		prove.remote.run_server(self.read_config())


def main():
	AgentDaemon().main()


if __name__ == '__main__':
	main()
