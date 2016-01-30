import logging
import sys


def setup_logging(config):
	log_level = logging.WARNING
	if 'log_level' in config:
		log_level = getattr(logging, config['log_level'].upper())
	root = logging.getLogger()
	root.setLevel(log_level)

	log_path = config.get('log_path', 'stdout')
	if not log_path or log_path == 'stdout':
		handler = logging.StreamHandler(sys.stdout)
	elif log_path == 'stderr':
		handler = logging.StreamHandler(sys.stderr)
	elif log_path:
		handler = logging.StreamHandler(log_path)

	handler.setLevel(log_level)

	# define the logging format
	formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
	handler.setFormatter(formatter)

	# add the logging handler for all loggers
	root.addHandler(handler)
