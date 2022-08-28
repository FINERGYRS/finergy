from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("core", "doctype", "domain")
	finergy.reload_doc("core", "doctype", "has_domain")
	active_domains = finergy.get_active_domains()
	all_domains = finergy.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = finergy.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
