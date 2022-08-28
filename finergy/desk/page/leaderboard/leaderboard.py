# Copyright (c) 2017, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import print_function, unicode_literals

import finergy


@finergy.whitelist()
def get_leaderboard_config():
	leaderboard_config = finergy._dict()
	leaderboard_hooks = finergy.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(finergy.get_attr(hook)())

	return leaderboard_config
