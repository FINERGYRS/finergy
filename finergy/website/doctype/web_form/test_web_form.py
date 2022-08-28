# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# See license.txt
from __future__ import unicode_literals

import json
import unittest

import finergy
from finergy.website.doctype.web_form.web_form import accept
from finergy.website.render import build_page

test_dependencies = ["Web Form"]


class TestWebForm(unittest.TestCase):
	def setUp(self):
		finergy.conf.disable_website_cache = True
		finergy.local.path = None

	def tearDown(self):
		finergy.conf.disable_website_cache = False
		finergy.local.path = None
		finergy.local.request_ip = None
		finergy.form_dict.web_form = None
		finergy.form_dict.data = None
		finergy.form_dict.docname = None

	def test_accept(self):
		finergy.set_user("Administrator")

		doc = {
			"doctype": "Event",
			"subject": "_Test Event Web Form",
			"description": "_Test Event Description",
			"starts_on": "2014-09-09",
		}

		finergy.form_dict.web_form = "manage-events"
		finergy.form_dict.data = json.dumps(doc)
		finergy.local.request_ip = "127.0.0.1"

		accept(web_form="manage-events", data=json.dumps(doc))

		self.event_name = finergy.db.get_value("Event", {"subject": "_Test Event Web Form"})
		self.assertTrue(self.event_name)

	def test_edit(self):
		self.test_accept()

		doc = {
			"doctype": "Event",
			"subject": "_Test Event Web Form",
			"description": "_Test Event Description 1",
			"starts_on": "2014-09-09",
			"name": self.event_name,
		}

		self.assertNotEquals(
			finergy.db.get_value("Event", self.event_name, "description"), doc.get("description")
		)

		finergy.form_dict.web_form = "manage-events"
		finergy.form_dict.docname = self.event_name
		finergy.form_dict.data = json.dumps(doc)

		accept(web_form="manage-events", docname=self.event_name, data=json.dumps(doc))

		self.assertEqual(
			finergy.db.get_value("Event", self.event_name, "description"), doc.get("description")
		)
