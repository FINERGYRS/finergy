# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy
import finergy.desk.form.document_follow as document_follow


class TestDocumentFollow(unittest.TestCase):
	def test_document_follow(self):
		user = get_user()
		event_doc = get_event()

		event_doc.description = "This is a test description for sending mail"
		event_doc.save(ignore_version=False)

		document_follow.unfollow_document("Event", event_doc.name, user.name)
		doc = document_follow.follow_document("Event", event_doc.name, user.name)
		self.assertEquals(doc.user, user.name)

		document_follow.send_hourly_updates()

		email_queue_entry_name = finergy.get_all("Email Queue", limit=1)[0].name
		email_queue_entry_doc = finergy.get_doc("Email Queue", email_queue_entry_name)

		self.assertEquals((email_queue_entry_doc.recipients[0].recipient), user.name)

		self.assertIn(event_doc.doctype, email_queue_entry_doc.message)
		self.assertIn(event_doc.name, email_queue_entry_doc.message)

	def tearDown(self):
		finergy.db.rollback()


def get_event():
	doc = finergy.get_doc(
		{
			"doctype": "Event",
			"subject": "_Test_Doc_Follow",
			"doc.starts_on": finergy.utils.now(),
			"doc.ends_on": finergy.utils.add_days(finergy.utils.now(), 5),
			"doc.description": "Hello",
		}
	)
	doc.insert()
	return doc


def get_user():
	if finergy.db.exists("User", "test@docsub.com"):
		doc = finergy.get_doc("User", "test@docsub.com")
	else:
		doc = finergy.new_doc("User")
		doc.email = "test@docsub.com"
		doc.first_name = "Test"
		doc.last_name = "User"
		doc.send_welcome_email = 0
		doc.document_follow_notify = 1
		doc.document_follow_frequency = "Hourly"
		doc.insert()
	return doc
