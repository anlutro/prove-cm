class StateGraphNode:
	def __init__(self, states, parent=None, children=None):
		if not isinstance(states, list):
			states = [states]
		self.states = states
		self.parent = parent
		self.children = children

	def __str__(self):
		if len(self.states) == 1:
			ret = self.states[0].name
		else:
			ret = '(' + '+'.join(s.name for s in self.states) + ')'
		if self.children:
			ret += ' -> '
			if len(self.children) == 1:
				ret += str(self.children[0])
			else:
				child_strs = []
				for node in self.children:
					if node.children:
						child_strs.append('(' + str(node) + ')')
					else:
						child_strs.append(str(node))
				delim = '+'
				if any(n.children for n in self.children):
					delim = ' + '
				ret += '(' + delim.join(child_strs) + ')'
		return ret


class StateGraph:
	def __init__(self, roots):
		self.roots = roots

	def __str__(self):
		return '\n'.join(str(node) for node in self.roots)


def generate_graph(state_list):
	avail_states = {}
	rev_requires = {}

	for state in state_list:
		avail_states[state.name] = state

		for require in state.requires:
			if require not in rev_requires:
				rev_requires[require] = []
			rev_requires[require].append(state.name)

	branch_endpoints = set()
	for state in state_list:
		# check if the state has no dependants (no states depend on it)
		if not rev_requires.get(state.name):
			branch_endpoints.add(state)

	added_states = []
	def make_node(states, parent=None):
		node = StateGraphNode(states, parent=parent)
		added_states.extend(states)

		requires = set()
		for state in states:
			if state.name in rev_requires:
				for state_require in rev_requires[state.name]:
					requires.add(state_require)
		if requires:
			requires = sorted(requires)
			require_states = [avail_states[require] for require in requires]
			node.children = [make_node(require_states, parent=node)]

		return node

	root_nodes = []
	for state in sorted(branch_endpoints):
		if state in added_states:
			continue

		states = [state]
		requires = state.requires

		# traverse up the tree until we find the root. a root is defined as a
		# state that does not depend on any other states
		while requires:
			states = list(set(avail_states[require] for require in requires))
			states.sort()
			requires = []
			for state in states:
				for state_require in state.requires:
					requires.append(state_require)

		root_nodes.append(make_node(states))

	return StateGraph(root_nodes)
