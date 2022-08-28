# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	finergy.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	finergy.delete_doc("Web Template", "Footer Horizontal", force=1)
