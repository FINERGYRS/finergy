import finergy


def execute():
	finergy.reload_doctype("Translation")
	finergy.db.sql(
		"UPDATE `tabTranslation` SET `translated_text`=`target_name`, `source_text`=`source_name`, `contributed`=0"
	)
