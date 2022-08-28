from __future__ import unicode_literals

import finergy


def execute():
	if not finergy.db.exists("Desk Page"):
		return

	pages = finergy.get_all(
		"Desk Page", filters={"is_standard": False}, fields=["name", "extends", "for_user"]
	)
	default_icon = {}
	for page in pages:
		if page.extends and page.for_user:
			if not default_icon.get(page.extends):
				default_icon[page.extends] = finergy.db.get_value("Desk Page", page.extends, "icon")

			icon = default_icon.get(page.extends)
			finergy.db.set_value("Desk Page", page.name, "icon", icon)
