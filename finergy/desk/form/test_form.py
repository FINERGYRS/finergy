# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import unittest

import finergy
from finergy.desk.form.linked_with import get_linked_docs, get_linked_doctypes


class TestForm(unittest.TestCase):
	def test_linked_with(self):
		results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
		self.assertTrue("User" in results)
		self.assertTrue("DocType" in results)


if __name__ == "__main__":
	finergy.connect()
	unittest.main()
