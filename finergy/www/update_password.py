# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

from finergy import _

no_cache = 1


def get_context(context):
	context.no_breadcrumbs = True
	context.parents = [{"name": "me", "title": _("My Account")}]
