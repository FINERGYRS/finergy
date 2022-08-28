# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.model.document import Document
from finergy.utils import cint


class BulkUpdate(Document):
	pass


@finergy.whitelist()
def update(doctype, field, value, condition="", limit=500):
	if not limit or cint(limit) > 500:
		limit = 500

	if condition:
		condition = " where " + condition

	if ";" in condition:
		finergy.throw(_("; not allowed in condition"))

	docnames = finergy.db.sql_list(
		"""select name from `tab{0}`{1} limit 0, {2}""".format(doctype, condition, limit)
	)
	data = {}
	data[field] = value
	return submit_cancel_or_update_docs(doctype, docnames, "update", data)


@finergy.whitelist()
def submit_cancel_or_update_docs(doctype, docnames, action="submit", data=None):
	docnames = finergy.parse_json(docnames)

	if data:
		data = finergy.parse_json(data)

	failed = []

	for i, d in enumerate(docnames, 1):
		doc = finergy.get_doc(doctype, d)
		try:
			message = ""
			if action == "submit" and doc.docstatus == 0:
				doc.submit()
				message = _("Submitting {0}").format(doctype)
			elif action == "cancel" and doc.docstatus == 1:
				doc.cancel()
				message = _("Cancelling {0}").format(doctype)
			elif action == "update" and doc.docstatus < 2:
				doc.update(data)
				doc.save()
				message = _("Updating {0}").format(doctype)
			else:
				failed.append(d)
			finergy.db.commit()
			show_progress(docnames, message, i, d)

		except Exception:
			failed.append(d)
			finergy.db.rollback()

	return failed


def show_progress(docnames, message, i, description):
	n = len(docnames)
	if n >= 10:
		finergy.publish_progress(float(i) * 100 / n, title=message, description=description)
