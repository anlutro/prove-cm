import prove.operations

from ..actions.cmd import CmdAction


class CmdCommand(prove.operations.Command):
	action_cls = CmdAction
