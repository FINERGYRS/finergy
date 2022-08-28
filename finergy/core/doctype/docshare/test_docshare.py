# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# See license.txt

from __future__ import unicode_literals

import unittest

import finergy
import finergy.share
from finergy.automation.doctype.auto_repeat.test_auto_repeat import create_submittable_doctype

test_dependencies = ["User"]


class TestDocShare(unittest.TestCase):
	def setUp(self):
		self.user = "test@example.com"
		self.event = finergy.get_doc(
			{
				"doctype": "Event",
				"subject": "test share event",
				"starts_on": "2015-01-01 10:00:00",
				"event_type": "Private",
			}
		).insert()

	def tearDown(self):
		finergy.set_user("Administrator")
		self.event.delete()

	def test_add(self):
		# user not shared
		self.assertTrue(self.event.name not in finergy.share.get_shared("Event", self.user))
		finergy.share.add("Event", self.event.name, self.user)
		self.assertTrue(self.event.name in finergy.share.get_shared("Event", self.user))

	def test_doc_permission(self):
		finergy.set_user(self.user)
		self.assertFalse(self.event.has_permission())

		finergy.set_user("Administrator")
		finergy.share.add("Event", self.event.name, self.user)

		finergy.set_user(self.user)
		self.assertTrue(self.event.has_permission())

	def test_share_permission(self):
		finergy.share.add("Event", self.event.name, self.user, write=1, share=1)

		finergy.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		# test cascade
		self.assertTrue(self.event.has_permission("read"))
		self.assertTrue(self.event.has_permission("write"))

	def test_set_permission(self):
		finergy.share.add("Event", self.event.name, self.user)

		finergy.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

		finergy.set_user("Administrator")
		finergy.share.set_permission("Event", self.event.name, self.user, "share")

		finergy.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

	def test_permission_to_share(self):
		finergy.set_user(self.user)
		self.assertRaises(finergy.PermissionError, finergy.share.add, "Event", self.event.name, self.user)

		finergy.set_user("Administrator")
		finergy.share.add("Event", self.event.name, self.user, write=1, share=1)

		# test not raises
		finergy.set_user(self.user)
		finergy.share.add("Event", self.event.name, "test1@example.com", write=1, share=1)

	def test_remove_share(self):
		finergy.share.add("Event", self.event.name, self.user, write=1, share=1)

		finergy.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		finergy.set_user("Administrator")
		finergy.share.remove("Event", self.event.name, self.user)

		finergy.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

	def test_share_with_everyone(self):
		self.assertTrue(self.event.name not in finergy.share.get_shared("Event", self.user))

		finergy.share.set_permission("Event", self.event.name, None, "read", everyone=1)
		self.assertTrue(self.event.name in finergy.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name in finergy.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in finergy.share.get_shared("Event", "Guest"))

		finergy.share.set_permission("Event", self.event.name, None, "read", value=0, everyone=1)
		self.assertTrue(self.event.name not in finergy.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name not in finergy.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in finergy.share.get_shared("Event", "Guest"))

	def test_share_with_submit_perm(self):
		doctype = "Test DocShare with Submit"
		create_submittable_doctype(doctype, submit_perms=0)

		submittable_doc = finergy.get_doc(
			dict(doctype=doctype, test="test docshare with submit")
		).insert()

		finergy.set_user(self.user)
		self.assertFalse(finergy.has_permission(doctype, "submit", user=self.user))

		finergy.set_user("Administrator")
		finergy.share.add(doctype, submittable_doc.name, self.user, submit=1)

		finergy.set_user(self.user)
		self.assertTrue(
			finergy.has_permission(doctype, "submit", doc=submittable_doc.name, user=self.user)
		)

		# test cascade
		self.assertTrue(finergy.has_permission(doctype, "read", doc=submittable_doc.name, user=self.user))
		self.assertTrue(
			finergy.has_permission(doctype, "write", doc=submittable_doc.name, user=self.user)
		)

		finergy.share.remove(doctype, submittable_doc.name, self.user)
