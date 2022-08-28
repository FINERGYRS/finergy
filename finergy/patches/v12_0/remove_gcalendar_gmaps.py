import finergy


def execute():
	"""
	Remove GCalendar and GCalendar Settings
	Remove Google Maps Settings as its been merged with Delivery Trips
	"""
	finergy.delete_doc_if_exists("DocType", "GCalendar Account")
	finergy.delete_doc_if_exists("DocType", "GCalendar Settings")
	finergy.delete_doc_if_exists("DocType", "Google Maps Settings")
