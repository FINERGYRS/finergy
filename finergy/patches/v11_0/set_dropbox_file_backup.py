from __future__ import unicode_literals

import finergy
from finergy.utils import cint


def execute():
	finergy.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(finergy.db.get_value("Dropbox Settings", None, "enabled"))
	if check_dropbox_enabled == 1:
		finergy.db.set_value("Dropbox Settings", None, "file_backup", 1)
