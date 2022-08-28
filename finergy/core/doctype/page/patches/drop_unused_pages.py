import finergy


def execute():
	for name in ("desktop", "space"):
		finergy.delete_doc("Page", name)
