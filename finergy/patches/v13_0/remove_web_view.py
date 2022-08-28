import finergy


def execute():
	finergy.delete_doc_if_exists("DocType", "Web View")
	finergy.delete_doc_if_exists("DocType", "Web View Component")
	finergy.delete_doc_if_exists("DocType", "CSS Class")
