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
	all_requires = {}
	reverse_requires = {}

	for state in state_list:
		avail_states[state.name] = state
		if state.name not in reverse_requires:
			reverse_requires[state.name] = []
		for require in state.requires:
			if require not in all_requires:
				all_requires[require] = []
			all_requires[require].append(state.name)
			reverse_requires[state.name].append(require)

	def make_node(state, parent=None):
		child_states = all_requires.get(state.name)
		if child_states:
			children = [
				make_node(avail_states[child_state], parent=state)
				for child_state in child_states
			]
		else:
			children = None
		node = StateGraphNode(state, parent=parent, children=children)
		return node

	root_nodes = []

	for state in state_list.copy():
		if not state.requires:
			root_nodes.append(make_node(state))

	return StateGraph(root_nodes)
