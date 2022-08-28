import finergy
from finergy.desk.utils import slug


def execute():
	for doctype in finergy.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			finergy.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
