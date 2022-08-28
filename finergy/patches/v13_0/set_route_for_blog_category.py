import finergy


def execute():
	categories = finergy.get_list("Blog Category")
	for category in categories:
		doc = finergy.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
