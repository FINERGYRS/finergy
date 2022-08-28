from __future__ import unicode_literals

import finergy
from finergy.model.rename_doc import rename_doc


def execute():
	if finergy.db.table_exists("Standard Reply") and not finergy.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		finergy.reload_doc("email", "doctype", "email_template")
