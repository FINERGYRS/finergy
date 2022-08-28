# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("core", "doctype", "DocField")

	if finergy.db.has_column("DocField", "show_days"):
		finergy.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		finergy.db.sql_ddl("alter table tabDocField drop column show_days")

	if finergy.db.has_column("DocField", "show_seconds"):
		finergy.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		finergy.db.sql_ddl("alter table tabDocField drop column show_seconds")

	finergy.clear_cache(doctype="DocField")
