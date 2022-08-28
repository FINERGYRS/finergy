# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import unittest

import finergy


class TestDocumentLocks(unittest.TestCase):
	def test_locking(self):
		todo = finergy.get_doc(dict(doctype="ToDo", description="test")).insert()
		todo_1 = finergy.get_doc("ToDo", todo.name)

		todo.lock()
		self.assertRaises(finergy.DocumentLockedError, todo_1.lock)
		todo.unlock()

		todo_1.lock()
		self.assertRaises(finergy.DocumentLockedError, todo.lock)
		todo_1.unlock()
