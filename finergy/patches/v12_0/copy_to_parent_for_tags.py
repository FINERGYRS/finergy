import finergy


def execute():

	finergy.db.sql("UPDATE `tabTag Link` SET parenttype=document_type")
	finergy.db.sql("UPDATE `tabTag Link` SET parent=document_name")
