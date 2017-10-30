import prove.operations

from ..actions.test import TestAction


class TestCommand(prove.operations.Command):
	action_cls = TestAction
