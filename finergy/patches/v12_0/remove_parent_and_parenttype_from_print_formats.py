import finergy


def execute():
	finergy.db.sql(
		"""
        UPDATE
            `tabPrint Format`
        SET
            `tabPrint Format`.`parent`='',
            `tabPrint Format`.`parenttype`='',
            `tabPrint Format`.parentfield=''
        WHERE
            `tabPrint Format`.parent != ''
            OR `tabPrint Format`.parenttype != ''
        """
	)
