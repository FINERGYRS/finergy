import finergy


def execute():
	"""
	Remove GSuite Template and GSuite Settings
	"""
	finergy.delete_doc_if_exists("DocType", "GSuite Settings")
	finergy.delete_doc_if_exists("DocType", "GSuite Templates")
