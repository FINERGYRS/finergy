# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

import finergy


def execute():
	finergy.reload_doc("core", "doctype", "system_settings", force=1)
	finergy.db.set_value("System Settings", None, "password_reset_limit", 3)
