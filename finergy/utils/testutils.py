# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import finergy


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	finergy.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	finergy.db.sql("delete from `tabCustom Field` where dt=%s", doctype)
	finergy.clear_cache(doctype=doctype)
