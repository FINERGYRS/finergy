from __future__ import unicode_literals

"""
Run this after updating country_info.json and or
"""
import finergy


def execute():
	for col in ("field", "doctype"):
		finergy.db.sql_ddl("alter table `tabSingles` modify column `{0}` varchar(255)".format(col))
