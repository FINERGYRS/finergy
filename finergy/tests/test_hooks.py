# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import unittest

import finergy
from finergy.cache_manager import clear_controller_cache
from finergy.desk.doctype.todo.todo import ToDo


class TestHooks(unittest.TestCase):
	def test_hooks(self):
		hooks = finergy.get_hooks()
		self.assertTrue(isinstance(hooks.get("app_name"), list))
		self.assertTrue(isinstance(hooks.get("doc_events"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(
			"finergy.desk.notifications.clear_doctype_notifications"
			in hooks.get("doc_events").get("*").get("on_update")
		)

	def test_override_doctype_class(self):
		from finergy import hooks

		# Set hook
		hooks.override_doctype_class = {"ToDo": ["finergy.tests.test_hooks.CustomToDo"]}

		# Clear cache
		finergy.cache().delete_value("app_hooks")
		clear_controller_cache("ToDo")

		todo = finergy.get_doc(doctype="ToDo", description="asdf")
		self.assertTrue(isinstance(todo, CustomToDo))

	def test_has_permission(self):
		from finergy import hooks

		# Set hook
		address_has_permission_hook = hooks.has_permission.get("Address", [])
		if isinstance(address_has_permission_hook, str):
			address_has_permission_hook = [address_has_permission_hook]

		address_has_permission_hook.append("finergy.tests.test_hooks.custom_has_permission")

		hooks.has_permission["Address"] = address_has_permission_hook

		# Clear cache
		finergy.cache().delete_value("app_hooks")

		# Init User and Address
		username = "test@example.com"
		user = finergy.get_doc("User", username)
		user.add_roles("System Manager")
		address = finergy.new_doc("Address")

		# Test!
		self.assertTrue(finergy.has_permission("Address", doc=address, user=username))

		address.flags.dont_touch_me = True
		self.assertFalse(finergy.has_permission("Address", doc=address, user=username))


def custom_has_permission(doc, ptype, user):
	if doc.flags.dont_touch_me:
		return False


class CustomToDo(ToDo):
	pass
