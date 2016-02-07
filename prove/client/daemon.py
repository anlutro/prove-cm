import argparse

import prove.client
import prove.remote.server


class DaemonClient(prove.client.AbstractClient):
	def __init__(self, args=None):
		parser = argparse.ArgumentParser(description="Prove - a configuration manager")
		parser.add_argument('-c', '--config',
			help="Path to config file")
		parser.add_argument('-l', '--log-level',
			help="Set the log level")
		parser.add_argument('--log-path',
			help="Set the log path")
		super().__init__(parser.parse_args(args))

	def main(self):
		self.read_config()
		prove.remote.server.run_server('0.0.0.0')


def main():
	DaemonClient().main()
