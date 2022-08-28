# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy
import finergy.utils.user
from finergy import _, throw
from finergy.model import data_fieldtypes
from finergy.permissions import check_admin_or_system_manager, rights


def execute(filters=None):
	user, doctype, show_permissions = (
		filters.get("user"),
		filters.get("doctype"),
		filters.get("show_permissions"),
	)

	if not validate(user, doctype):
		return [], []

	columns, fields = get_columns_and_fields(doctype)
	data = finergy.get_list(doctype, fields=fields, as_list=True, user=user)

	if show_permissions:
		columns = columns + [finergy.unscrub(right) + ":Check:80" for right in rights]
		data = list(data)
		for i, doc in enumerate(data):
			permission = finergy.permissions.get_doc_permissions(finergy.get_doc(doctype, doc[0]), user)
			data[i] = doc + tuple(permission.get(right) for right in rights)

	return columns, data


def validate(user, doctype):
	# check if current user is System Manager
	check_admin_or_system_manager()
	return user and doctype


def get_columns_and_fields(doctype):
	columns = ["Name:Link/{}:200".format(doctype)]
	fields = ["`name`"]
	for df in finergy.get_meta(doctype).fields:
		if df.in_list_view and df.fieldtype in data_fieldtypes:
			fields.append("`{0}`".format(df.fieldname))
			fieldtype = "Link/{}".format(df.options) if df.fieldtype == "Link" else df.fieldtype
			columns.append(
				"{label}:{fieldtype}:{width}".format(
					label=df.label, fieldtype=fieldtype, width=df.width or 100
				)
			)

	return columns, fields


@finergy.whitelist()
@finergy.validate_and_sanitize_search_inputs
def query_doctypes(doctype, txt, searchfield, start, page_len, filters):
	user = filters.get("user")
	user_perms = finergy.utils.user.UserPermissions(user)
	user_perms.build_permissions()
	can_read = user_perms.can_read  # Does not include child tables

	single_doctypes = [d[0] for d in finergy.db.get_values("DocType", {"issingle": 1})]

	out = []
	for dt in can_read:
		if txt.lower().replace("%", "") in dt.lower() and dt not in single_doctypes:
			out.append([dt])

	return out
