# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy


class TestViewLog(unittest.TestCase):
	def tearDown(self):
		finergy.set_user("Administrator")

	def test_if_user_is_added(self):
		ev = finergy.get_doc(
			{
				"doctype": "Event",
				"subject": "test event for view logs",
				"starts_on": "2018-06-04 14:11:00",
				"event_type": "Public",
			}
		).insert()

		finergy.set_user("test@example.com")

		from finergy.desk.form.load import getdoc

		# load the form
		getdoc("Event", ev.name)
		a = finergy.get_value(
			doctype="View Log",
			filters={"reference_doctype": "Event", "reference_name": ev.name},
			fieldname=["viewed_by"],
		)

		self.assertEqual("test@example.com", a)
		self.assertNotEqual("test1@example.com", a)
