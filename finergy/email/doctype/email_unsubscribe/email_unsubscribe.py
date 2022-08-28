# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Reporting Solutions SAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.model.document import Document


class EmailUnsubscribe(Document):
	def validate(self):
		if not self.global_unsubscribe and not (self.reference_doctype and self.reference_name):
			finergy.throw(_("Reference DocType and Reference Name are required"), finergy.MandatoryError)

		if not self.global_unsubscribe and finergy.db.get_value(
			self.doctype, self.name, "global_unsubscribe"
		):
			finergy.throw(_("Delete this record to allow sending to this email address"))

		if self.global_unsubscribe:
			if finergy.get_all(
				"Email Unsubscribe",
				filters={"email": self.email, "global_unsubscribe": 1, "name": ["!=", self.name]},
			):
				finergy.throw(_("{0} already unsubscribed").format(self.email), finergy.DuplicateEntryError)

		else:
			if finergy.get_all(
				"Email Unsubscribe",
				filters={
					"email": self.email,
					"reference_doctype": self.reference_doctype,
					"reference_name": self.reference_name,
					"name": ["!=", self.name],
				},
			):
				finergy.throw(
					_("{0} already unsubscribed for {1} {2}").format(
						self.email, self.reference_doctype, self.reference_name
					),
					finergy.DuplicateEntryError,
				)

	def on_update(self):
		if self.reference_doctype and self.reference_name:
			doc = finergy.get_doc(self.reference_doctype, self.reference_name)
			doc.add_comment("Label", _("Left this conversation"), comment_email=self.email)
