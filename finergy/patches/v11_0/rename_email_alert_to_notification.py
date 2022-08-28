from __future__ import unicode_literals

import finergy
from finergy.model.rename_doc import rename_doc


def execute():
	if finergy.db.table_exists("Email Alert Recipient") and not finergy.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		finergy.reload_doc("email", "doctype", "notification_recipient")

	if finergy.db.table_exists("Email Alert") and not finergy.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		finergy.reload_doc("email", "doctype", "notification")
