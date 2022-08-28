import finergy
from finergy.model.utils.rename_field import rename_field


def execute():
	if not finergy.db.table_exists("Dashboard Chart"):
		return

	finergy.reload_doc("desk", "doctype", "dashboard_chart")

	if finergy.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
