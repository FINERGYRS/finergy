# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import print_function, unicode_literals

import finergy

no_cache = 1


def get_context(context):
	if finergy.flags.in_migrate:
		return
	context.http_status_code = 500
	print(finergy.get_traceback())
	return {"error": finergy.get_traceback().replace("<", "&lt;").replace(">", "&gt;")}
