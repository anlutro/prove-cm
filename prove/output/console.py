import sys
import textwrap


def rendering_states(host):
	sys.stdout.write('[{}] Rendering states... '.format(host))
	sys.stdout.flush()


def start_connect():
	sys.stdout.write('Connecting... ')
	sys.stdout.flush()


def connect_error(msg):
	msg = '[\033[31mERROR\033[0m] Encountered an error when trying to connect: ' + msg
	sys.stdout.write('\n' + textwrap.fill(msg, 80) + '\n')


def finish_connect():
	print('Connected!')


def start_state(state_id, state_fn):
	sys.stdout.write('├─ Running {} ({})... '.format(state_id, state_fn))
	sys.stdout.flush()


def state_error(exception):
	print('\033[31m' + 'Error!' + '\033[0m')
	print('│  └─ ' + str(exception))


def finish_state(result, comment):
	color = '\033[32m' if result else '\033[31m'
	reset = '\033[0m'
	if not isinstance(comment, list):
		if '\n' in comment:
			comment = comment.splitlines()
		elif comment:
			comment = [comment]
		else:
			comment = []
	# remove empty strings from list
	comment = [c for c in comment if c]
	if comment:
		comment_out = '│  └─ ' + comment[0]
		if len(comment) > 1:
			comment_lines = ['│     ' + line for line in comment[1:] if line]
			comment_out += '\n' + '\n'.join(comment_lines)
		comment = comment_out.rstrip()

	if result:
		print(color + 'Success!' + reset)
	else:
		print(color + 'Failure!' + reset)
	if comment:
		sys.stdout.write(comment + '\n')
	sys.stdout.write('\033[0m')


def finish_run(num_succeeded_states, num_failed_states):
	if num_failed_states > 0:
		print('└─ \033[31m{} states failed, {} succeeded\033[0m'.format(num_failed_states, num_succeeded_states))
	else:
		print('└─ \033[32m{} states successfully ran!\033[0m'.format(num_succeeded_states))
