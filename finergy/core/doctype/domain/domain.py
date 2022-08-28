# -*- coding: utf-8 -*-
# Copyright (c) 2017, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.custom.doctype.custom_field.custom_field import create_custom_fields
from finergy.model.document import Document


class Domain(Document):
	"""Domain documents are created automatically when DocTypes
	with "Restricted" domains are imported during
	installation or migration"""

	def setup_domain(self):
		"""Setup domain icons, permissions, custom fields etc."""
		self.setup_data()
		self.setup_roles()
		self.setup_properties()
		self.set_values()

		if not int(finergy.defaults.get_defaults().setup_complete or 0):
			# if setup not complete, setup desktop etc.
			self.setup_sidebar_items()
			self.set_default_portal_role()

		if self.data.custom_fields:
			create_custom_fields(self.data.custom_fields)

		if self.data.on_setup:
			# custom on_setup method
			finergy.get_attr(self.data.on_setup)()

	def remove_domain(self):
		"""Unset domain settings"""
		self.setup_data()

		if self.data.restricted_roles:
			for role_name in self.data.restricted_roles:
				if finergy.db.exists("Role", role_name):
					role = finergy.get_doc("Role", role_name)
					role.disabled = 1
					role.save()

		self.remove_custom_field()

	def remove_custom_field(self):
		"""Remove custom_fields when disabling domain"""
		if self.data.custom_fields:
			for doctype in self.data.custom_fields:
				custom_fields = self.data.custom_fields[doctype]

				# custom_fields can be a list or dict
				if isinstance(custom_fields, dict):
					custom_fields = [custom_fields]

				for custom_field_detail in custom_fields:
					custom_field_name = finergy.db.get_value(
						"Custom Field", dict(dt=doctype, fieldname=custom_field_detail.get("fieldname"))
					)
					if custom_field_name:
						finergy.delete_doc("Custom Field", custom_field_name)

	def setup_roles(self):
		"""Enable roles that are restricted to this domain"""
		if self.data.restricted_roles:
			user = finergy.get_doc("User", finergy.session.user)
			for role_name in self.data.restricted_roles:
				user.append("roles", {"role": role_name})
				if not finergy.db.get_value("Role", role_name):
					finergy.get_doc(dict(doctype="Role", role_name=role_name)).insert()
					continue

				role = finergy.get_doc("Role", role_name)
				role.disabled = 0
				role.save()
			user.save()

	def setup_data(self, domain=None):
		"""Load domain info via hooks"""
		self.data = finergy.get_domain_data(self.name)

	def get_domain_data(self, module):
		return finergy.get_attr(finergy.get_hooks("domains")[self.name] + ".data")

	def set_default_portal_role(self):
		"""Set default portal role based on domain"""
		if self.data.get("default_portal_role"):
			finergy.db.set_value(
				"Portal Settings", None, "default_role", self.data.get("default_portal_role")
			)

	def setup_properties(self):
		if self.data.properties:
			for args in self.data.properties:
				finergy.make_property_setter(args)

	def set_values(self):
		"""set values based on `data.set_value`"""
		if self.data.set_value:
			for args in self.data.set_value:
				finergy.reload_doctype(args[0])
				doc = finergy.get_doc(args[0], args[1] or args[0])
				doc.set(args[2], args[3])
				doc.save()

	def setup_sidebar_items(self):
		"""Enable / disable sidebar items"""
		if self.data.allow_sidebar_items:
			# disable all
			finergy.db.sql("update `tabPortal Menu Item` set enabled=0")

			# enable
			finergy.db.sql(
				"""update `tabPortal Menu Item` set enabled=1
				where route in ({0})""".format(
					", ".join(['"{0}"'.format(d) for d in self.data.allow_sidebar_items])
				)
			)

		if self.data.remove_sidebar_items:
			# disable all
			finergy.db.sql("update `tabPortal Menu Item` set enabled=1")

			# enable
			finergy.db.sql(
				"""update `tabPortal Menu Item` set enabled=0
				where route in ({0})""".format(
					", ".join(['"{0}"'.format(d) for d in self.data.remove_sidebar_items])
				)
			)
