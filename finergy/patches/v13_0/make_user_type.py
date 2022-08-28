import finergy
from finergy.utils.install import create_user_type


def execute():
	finergy.reload_doc("core", "doctype", "role")
	finergy.reload_doc("core", "doctype", "user_document_type")
	finergy.reload_doc("core", "doctype", "user_type_module")
	finergy.reload_doc("core", "doctype", "user_select_document_type")
	finergy.reload_doc("core", "doctype", "user_type")

	create_user_type()
