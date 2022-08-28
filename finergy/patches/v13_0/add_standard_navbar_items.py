from __future__ import unicode_literals

import finergy
from finergy.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for CapKPI in Navbar Settings
	finergy.reload_doc("core", "doctype", "navbar_settings")
	finergy.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
