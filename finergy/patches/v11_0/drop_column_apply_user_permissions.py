from __future__ import unicode_literals

import finergy


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if finergy.db.table_exists(doctype):
			if column in finergy.db.get_table_columns(doctype):
				finergy.db.sql("alter table `tab{0}` drop column {1}".format(doctype, column))

	finergy.reload_doc("core", "doctype", "docperm", force=True)
	finergy.reload_doc("core", "doctype", "custom_docperm", force=True)
