from __future__ import unicode_literals

import finergy


def execute():
	if finergy.db.table_exists("Prepared Report"):
		finergy.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = finergy.get_all("Prepared Report")
		for report in prepared_reports:
			finergy.delete_doc("Prepared Report", report.name)
