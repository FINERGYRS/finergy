# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	if not finergy.db.table_exists("Data Import"):
		return

	meta = finergy.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	finergy.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	finergy.rename_doc("DocType", "Data Import", "Data Import Legacy")
	finergy.db.commit()
	finergy.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	finergy.rename_doc("DocType", "Data Import Beta", "Data Import")
