import os
import os.path
import sys

import prove.client


def main():
	args = sys.argv[1:]

	for arg in args:
		if not arg.startswith('-'):
			config_path = arg
			args.remove(config_path)
			break
	else:
		config_path = os.path.join(os.getcwd(), 'prove.yml')

	prove.client.Client.from_config_file(config_path, args).run()


if __name__ == '__main__':
	main()
