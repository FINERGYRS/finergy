# -*- coding: utf-8 -*-
# Copyright (c) 2017, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class DomainSettings(Document):
	def set_active_domains(self, domains):
		active_domains = [d.domain for d in self.active_domains]
		added = False
		for d in domains:
			if not d in active_domains:
				self.append("active_domains", dict(domain=d))
				added = True

		if added:
			self.save()

	def on_update(self):
		for i, d in enumerate(self.active_domains):
			# set the flag to update the the desktop icons of all domains
			if i >= 1:
				finergy.flags.keep_desktop_icons = True
			domain = finergy.get_doc("Domain", d.domain)
			domain.setup_domain()

		self.restrict_roles_and_modules()
		finergy.clear_cache()

	def restrict_roles_and_modules(self):
		"""Disable all restricted roles and set `restrict_to_domain` property in Module Def"""
		active_domains = finergy.get_active_domains()
		all_domains = list((finergy.get_hooks("domains") or {}))

		def remove_role(role):
			finergy.db.sql("delete from `tabHas Role` where role=%s", role)
			finergy.set_value("Role", role, "disabled", 1)

		for domain in all_domains:
			data = finergy.get_domain_data(domain)
			if not finergy.db.get_value("Domain", domain):
				finergy.get_doc(dict(doctype="Domain", domain=domain)).insert()
			if "modules" in data:
				for module in data.get("modules"):
					finergy.db.set_value("Module Def", module, "restrict_to_domain", domain)

			if "restricted_roles" in data:
				for role in data["restricted_roles"]:
					if not finergy.db.get_value("Role", role):
						finergy.get_doc(dict(doctype="Role", role_name=role)).insert()
					finergy.db.set_value("Role", role, "restrict_to_domain", domain)

					if domain not in active_domains:
						remove_role(role)

			if "custom_fields" in data:
				if domain not in active_domains:
					inactive_domain = finergy.get_doc("Domain", domain)
					inactive_domain.setup_data()
					inactive_domain.remove_custom_field()


def get_active_domains():
	"""get the domains set in the Domain Settings as active domain"""

	def _get_active_domains():
		domains = finergy.get_all(
			"Has Domain", filters={"parent": "Domain Settings"}, fields=["domain"], distinct=True
		)

		active_domains = [row.get("domain") for row in domains]
		active_domains.append("")
		return active_domains

	return finergy.cache().get_value("active_domains", _get_active_domains)


def get_active_modules():
	"""get the active modules from Module Def"""

	def _get_active_modules():
		active_modules = []
		active_domains = get_active_domains()
		for m in finergy.get_all("Module Def", fields=["name", "restrict_to_domain"]):
			if (not m.restrict_to_domain) or (m.restrict_to_domain in active_domains):
				active_modules.append(m.name)
		return active_modules

	return finergy.cache().get_value("active_modules", _get_active_modules)
