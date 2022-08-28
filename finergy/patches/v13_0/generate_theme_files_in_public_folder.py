# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("website", "doctype", "website_theme_ignore_app")
	themes = finergy.db.get_all(
		"Website Theme", filters={"theme_url": ("not like", "/files/website_theme/%")}
	)
	for theme in themes:
		doc = finergy.get_doc("Website Theme", theme.name)
		try:
			doc.generate_bootstrap_theme()
			doc.save()
		except Exception:
			print("Ignoring....")
			print(finergy.get_traceback())
