# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import finergy
from finergy import _
from finergy.desk.doctype.bulk_update.bulk_update import show_progress
from finergy.model.document import Document


class DeletedDocument(Document):
	pass


@finergy.whitelist()
def restore(name, alert=True):
	deleted = finergy.get_doc("Deleted Document", name)

	if deleted.restored:
		finergy.throw(_("Document {0} Already Restored").format(name), exc=finergy.DocumentAlreadyRestored)

	doc = finergy.get_doc(json.loads(deleted.data))

	try:
		doc.insert()
	except finergy.DocstatusTransitionError:
		finergy.msgprint(_("Cancelled Document restored as Draft"))
		doc.docstatus = 0
		doc.insert()

	doc.add_comment("Edit", _("restored {0} as {1}").format(deleted.deleted_name, doc.name))

	deleted.new_name = doc.name
	deleted.restored = 1
	deleted.db_update()

	if alert:
		finergy.msgprint(_("Document Restored"))


@finergy.whitelist()
def bulk_restore(docnames):
	docnames = finergy.parse_json(docnames)
	message = _("Restoring Deleted Document")
	restored, invalid, failed = [], [], []

	for i, d in enumerate(docnames):
		try:
			show_progress(docnames, message, i + 1, d)
			restore(d, alert=False)
			finergy.db.commit()
			restored.append(d)

		except finergy.DocumentAlreadyRestored:
			finergy.message_log.pop()
			invalid.append(d)

		except Exception:
			finergy.message_log.pop()
			failed.append(d)
			finergy.db.rollback()

	return {"restored": restored, "invalid": invalid, "failed": failed}
