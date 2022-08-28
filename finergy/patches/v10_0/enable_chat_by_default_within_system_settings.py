from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doctype("System Settings")
	doc = finergy.get_single("System Settings")
	doc.enable_chat = 1

	# Changes prescribed by Nabin Hait (nabin@finergy-rs.fr)
	doc.flags.ignore_mandatory = True
	doc.flags.ignore_permissions = True

	doc.save()
