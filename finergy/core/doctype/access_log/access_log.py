# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and contributors
# For license information, please see license.txt

# imports - standard imports
from __future__ import unicode_literals

# imports - module imports
import finergy
from finergy.model.document import Document


class AccessLog(Document):
	pass


@finergy.whitelist()
def make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	_make_access_log(
		doctype,
		document,
		method,
		file_type,
		report_name,
		filters,
		page,
		columns,
	)


@finergy.write_only()
def _make_access_log(
	doctype=None,
	document=None,
	method=None,
	file_type=None,
	report_name=None,
	filters=None,
	page=None,
	columns=None,
):
	user = finergy.session.user
	in_request = finergy.request and finergy.request.method == "GET"

	doc = finergy.get_doc(
		{
			"doctype": "Access Log",
			"user": user,
			"export_from": doctype,
			"reference_document": document,
			"file_type": file_type,
			"report_name": report_name,
			"page": page,
			"method": method,
			"filters": finergy.utils.cstr(filters) if filters else None,
			"columns": columns,
		}
	)
	doc.insert(ignore_permissions=True)

	# `finergy.db.commit` added because insert doesnt `commit` when called in GET requests like `printview`
	# dont commit in test mode. It must be tempting to put this block along with the in_request in the
	# whitelisted method...yeah, don't do it. That part would be executed possibly on a read only DB conn
	if not finergy.flags.in_test or in_request:
		finergy.db.commit()
