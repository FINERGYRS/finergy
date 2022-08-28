import finergy


def execute():
	finergy.reload_doc("core", "doctype", "doctype_link")
	finergy.reload_doc("core", "doctype", "doctype_action")
	finergy.reload_doc("core", "doctype", "doctype")
	finergy.model.delete_fields(
		{"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1
	)

	finergy.db.sql(
		"""
		DELETE from `tabProperty Setter`
		WHERE property = 'read_only_onload'
	"""
	)
