import finergy


def execute():
	finergy.reload_doc("website", "doctype", "web_page_view", force=True)
	finergy.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
