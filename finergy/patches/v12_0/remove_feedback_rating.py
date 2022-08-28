import finergy


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	finergy.delete_doc("DocType", "Feedback Trigger")
	finergy.delete_doc("DocType", "Feedback Rating")
