def sort_states(states):
	min_priority = 0
	max_priority = 0
	state_priorities = {}
	requires = {}

	# find the minimum and maximum priority numbers. these are used to give a
	# number to "first" and "last" states
	for state_id, state_fn, state_args in states:
		if '_priority' in state_args and isinstance(state_args['_priority'], int):
			if  state_args['_priority'] > max_priority:
				max_priority = int(state_args['_priority']) + 1
			if state_args['_priority'] < min_priority:
				min_priority = int(state_args['_priority']) - 1
		if '_require' in state_args:
			if not isinstance(state_args['_require'], list):
				state_args['_require'] = [state_args['_require']]
			requires[state_id] = state_args.pop('_require')

	# states with no priority should come after max_priority, but before "last"
	default_state_priority = max_priority
	# remove any risk of overlapping between un-priorityed and "last" states
	max_priority += len(states)

	for state_id, state_fn, state_args in states:
		state_priority = default_state_priority
		if '_priority' in state_args:
			if state_args['_priority'] == 'first':
				min_priority -= 1
				state_priority = min_priority
			elif state_args['_priority'] == 'last':
				max_priority += 1
				state_priority = max_priority
			else:
				state_priority = int(state_args['_priority'])
		else:
			state_priority = default_state_priority
			default_state_priority += 1

		state_args['__priority'] = state_priority * 100
		state_priorities[state_id] = state_args['__priority']

	def get_state_priority(state):
		state_id, state_fn, state_args = state
		if state_id in requires:
			max_required_priority = None
			requirements = requires[state_id]
			for required_state in requires[state_id]:
				if required_state in requires:
					requirements += requires[required_state]
			for required_state in requirements:
				if max_required_priority is None or state_priorities[required_state] > max_required_priority:
					max_required_priority = state_priorities[required_state]
			if '_priority' in state_args and state_priorities[state_id] > max_required_priority:
				raise Exception('State priority cannot be higher than its requirements')
			state_args['__priority'] = max_required_priority + len(requirements)
			state_priorities[state_id] = state_args['__priority']
		return state_args['__priority']

	return sorted(states, key=get_state_priority)
