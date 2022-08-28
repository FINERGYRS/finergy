import finergy


def execute():
	doctype = "Top Bar Item"
	if not finergy.db.table_exists(doctype) or not finergy.db.has_column(doctype, "target"):
		return

	finergy.reload_doc("website", "doctype", "top_bar_item")
	finergy.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
