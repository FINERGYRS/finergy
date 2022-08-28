import finergy
from finergy.model.rename_doc import rename_doc


def execute():
	if finergy.db.exists("DocType", "Client Script"):
		return

	finergy.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	finergy.flags.ignore_route_conflict_validation = False

	finergy.reload_doctype("Client Script", force=True)
