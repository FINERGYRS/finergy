import finergy

from ..role import desk_properties


def execute():
	finergy.reload_doctype("user")
	finergy.reload_doctype("role")
	for role in finergy.get_all("Role", ["name", "desk_access"]):
		role_doc = finergy.get_doc("Role", role.name)
		for key in desk_properties:
			role_doc.set(key, role_doc.desk_access)
		role_doc.save()
