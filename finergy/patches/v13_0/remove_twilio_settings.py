# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

import finergy


def execute():
	"""Add missing Twilio patch.

	While making Twilio as a standaone app, we missed to delete Twilio records from DB through migration. Adding the missing patch.
	"""
	finergy.delete_doc_if_exists("DocType", "Twilio Number Group")
	if twilio_settings_doctype_in_integrations():
		finergy.delete_doc_if_exists("DocType", "Twilio Settings")
		finergy.db.sql("delete from `tabSingles` where `doctype`=%s", "Twilio Settings")


def twilio_settings_doctype_in_integrations() -> bool:
	"""Check Twilio Settings doctype exists in integrations module or not."""
	return finergy.db.exists("DocType", {"name": "Twilio Settings", "module": "Integrations"})
