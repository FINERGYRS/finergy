from __future__ import unicode_literals

import finergy
from finergy.model.rename_doc import rename_doc


def execute():
	if finergy.db.exists("DocType", "Google Maps") and not finergy.db.exists(
		"DocType", "Google Maps Settings"
	):
		rename_doc("DocType", "Google Maps", "Google Maps Settings")
