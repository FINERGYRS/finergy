# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.email.queue import send_one
from finergy.model.document import Document
from finergy.utils import sbool


class EmailQueue(Document):
	def set_recipients(self, recipients):
		self.set("recipients", [])
		for r in recipients:
			self.append("recipients", {"recipient": r, "status": "Not Sent"})

	def on_trash(self):
		self.prevent_email_queue_delete()

	def prevent_email_queue_delete(self):
		if finergy.session.user != "Administrator":
			finergy.throw(_("Only Administrator can delete Email Queue"))

	def get_duplicate(self, recipients):
		values = self.as_dict()
		del values["name"]
		duplicate = finergy.get_doc(values)
		duplicate.set_recipients(recipients)
		return duplicate


@finergy.whitelist()
def retry_sending(name):
	doc = finergy.get_doc("Email Queue", name)
	doc.check_permission()

	if doc and (doc.status == "Error" or doc.status == "Partially Errored"):
		doc.status = "Not Sent"
		for d in doc.recipients:
			if d.status != "Sent":
				d.status = "Not Sent"
		doc.save(ignore_permissions=True)


@finergy.whitelist()
def send_now(name):
	finergy.has_permission("Email Queue", doc=name, throw=True)
	send_one(name, now=True)


@finergy.whitelist()
def toggle_sending(enable):
	finergy.only_for("System Manager")
	finergy.db.set_default("suspend_email_queue", 0 if sbool(enable) else 1)


def on_doctype_update():
	"""Add index in `tabCommunication` for `(reference_doctype, reference_name)`"""
	finergy.db.add_index(
		"Email Queue", ("status", "send_after", "priority", "creation"), "index_bulk_flush"
	)
