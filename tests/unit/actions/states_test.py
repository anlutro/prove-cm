from unittest import mock

from tests.unit.actions import make_app_conn

import prove.actions.states


def test_StatesAction():
	action = prove.actions.states.StatesAction(args=[])
	app, _ = make_app_conn([])
	action.run(app=app)
	# TODO: assertions!
