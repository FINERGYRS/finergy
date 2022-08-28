# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	"""Set default module for standard Web Template, if none."""
	finergy.reload_doc("website", "doctype", "Web Template Field")
	finergy.reload_doc("website", "doctype", "web_template")

	standard_templates = finergy.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = finergy.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
