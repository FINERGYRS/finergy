from __future__ import unicode_literals

import finergy

base_template_path = "templates/www/robots.txt"


def get_context(context):
	robots_txt = (
		finergy.db.get_single_value("Website Settings", "robots_txt")
		or (finergy.local.conf.robots_txt and finergy.read_file(finergy.local.conf.robots_txt))
		or ""
	)

	return {"robots_txt": robots_txt}
