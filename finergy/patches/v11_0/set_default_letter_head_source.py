from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	finergy.db.sql("update `tabLetter Head` set source = 'HTML'")
