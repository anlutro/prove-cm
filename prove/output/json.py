import json


_data = {}
_current_host = None
_current_state_id = None


def start_connect(host):
	global _data
	global _current_host
	_current_host = host
	_data[host] = {}


def finish_connect():
	pass


def start_state(state_id, state_fn):
	global _current_state_id
	_current_state_id = state_id


def finish_state(result, comment):
	global _data
	global _current_host
	global _current_state_id
	if _current_state_id not in _data[_current_host]:
		_data[_current_host][_current_state_id] = []
	_data[_current_host][_current_state_id].append({
		'result': result,
		'comment': comment,
	})


def finish_run(num_succeeded_states, num_failed_states):
	print(json.dumps(_data))
