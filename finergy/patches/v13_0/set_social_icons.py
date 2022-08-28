import finergy


def execute():
	providers = finergy.get_all("Social Login Key")

	for provider in providers:
		doc = finergy.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
