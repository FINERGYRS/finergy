import finergy


def execute():
	finergy.db.sql(
		"""
        DELETE from `tabDocType`
        WHERE name = 'Feedback Request'
    """
	)
