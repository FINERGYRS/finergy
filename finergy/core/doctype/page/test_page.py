# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy

test_records = finergy.get_test_records("Page")


class TestPage(unittest.TestCase):
	def test_naming(self):
		self.assertRaises(
			finergy.NameError,
			finergy.get_doc(dict(doctype="Page", page_name="DocType", module="Core")).insert,
		)
		self.assertRaises(
			finergy.NameError,
			finergy.get_doc(dict(doctype="Page", page_name="Settings", module="Core")).insert,
		)
