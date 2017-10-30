import prove.operations

from ..actions.state import StateAction


class StateCommand(prove.operations.Command):
	action_cls = StateAction
