import finergy


def execute():
	finergy.reload_doc("website", "doctype", "website_theme_ignore_app")
	finergy.reload_doc("website", "doctype", "color")
	finergy.reload_doc("website", "doctype", "website_theme", force=True)

	for theme in finergy.get_all("Website Theme"):
		doc = finergy.get_doc("Website Theme", theme.name)
		if not doc.get("custom_scss") and doc.theme_scss:
			# move old theme to new theme
			doc.custom_scss = doc.theme_scss

			if doc.background_color:
				setup_color_record(doc.background_color)

			doc.save()


def setup_color_record(color):
	finergy.get_doc(
		{
			"doctype": "Color",
			"__newname": color,
			"color": color,
		}
	).save()
