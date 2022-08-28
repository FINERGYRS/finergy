# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

"""docfield utililtes"""

import finergy


def rename(doctype, fieldname, newname):
	"""rename docfield"""
	df = finergy.db.sql(
		"""select * from tabDocField where parent=%s and fieldname=%s""", (doctype, fieldname), as_dict=1
	)
	if not df:
		return

	df = df[0]

	if finergy.db.get_value("DocType", doctype, "issingle"):
		update_single(df, newname)
	else:
		update_table(df, newname)
		update_parent_field(df, newname)


def update_single(f, new):
	"""update in tabSingles"""
	finergy.db.begin()
	finergy.db.sql(
		"""update tabSingles set field=%s where doctype=%s and field=%s""",
		(new, f["parent"], f["fieldname"]),
	)
	finergy.db.commit()


def update_table(f, new):
	"""update table"""
	query = get_change_column_query(f, new)
	if query:
		finergy.db.sql(query)


def update_parent_field(f, new):
	"""update 'parentfield' in tables"""
	if f["fieldtype"] in finergy.model.table_fields:
		finergy.db.begin()
		finergy.db.sql(
			"""update `tab%s` set parentfield=%s where parentfield=%s""" % (f["options"], "%s", "%s"),
			(new, f["fieldname"]),
		)
		finergy.db.commit()


def get_change_column_query(f, new):
	"""generate change fieldname query"""
	desc = finergy.db.sql("desc `tab%s`" % f["parent"])
	for d in desc:
		if d[0] == f["fieldname"]:
			return "alter table `tab%s` change `%s` `%s` %s" % (f["parent"], f["fieldname"], new, d[1])


def supports_translation(fieldtype):
	return fieldtype in ["Data", "Select", "Text", "Small Text", "Text Editor"]
