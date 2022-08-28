# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("core", "doctype", "system_settings")
	finergy.db.set_value("System Settings", None, "allow_login_after_fail", 60)
