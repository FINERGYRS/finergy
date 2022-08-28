from __future__ import unicode_literals

import finergy
from finergy.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	finergy.reload_doc("desk", "doctype", "notification_settings")
	finergy.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = finergy.db.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
