# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy
import finergy.www.list
from finergy import _

no_cache = 1


def get_context(context):
	if finergy.session.user == "Guest":
		finergy.throw(_("You need to be logged in to access this page"), finergy.PermissionError)

	context.show_sidebar = True
