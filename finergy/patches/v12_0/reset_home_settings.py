import finergy


def execute():
	finergy.reload_doc("core", "doctype", "user")
	finergy.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
