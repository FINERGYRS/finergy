import finergy
from finergy.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes


def execute():
	finergy.reload_doc("desk", "doctype", "global_search_doctype")
	finergy.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()
