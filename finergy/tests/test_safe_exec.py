from __future__ import unicode_literals

import unittest

import finergy
from finergy.utils.safe_exec import get_safe_globals, safe_exec


class TestSafeExec(unittest.TestCase):
	def test_import_fails(self):
		self.assertRaises(ImportError, safe_exec, "import os")

	def test_internal_attributes(self):
		self.assertRaises(SyntaxError, safe_exec, "().__class__.__call__")

	def test_utils(self):
		_locals = dict(out=None)
		safe_exec("""out = finergy.utils.cint("1")""", None, _locals)
		self.assertEqual(_locals["out"], 1)

	def test_safe_eval(self):
		self.assertEqual(finergy.safe_eval("1+1"), 2)
		self.assertRaises(AttributeError, finergy.safe_eval, "finergy.utils.os.path", get_safe_globals())

	def test_sql(self):
		_locals = dict(out=None)
		safe_exec(
			"""out = finergy.db.sql("select name from tabDocType where name='DocType'")""", None, _locals
		)
		self.assertEqual(_locals["out"][0][0], "DocType")

		self.assertRaises(
			finergy.PermissionError, safe_exec, 'finergy.db.sql("update tabToDo set description=NULL")'
		)

	def test_call(self):
		# call non whitelisted method
		self.assertRaises(finergy.PermissionError, safe_exec, """finergy.call("finergy.get_user")""")

		# call whitelisted method
		safe_exec("""finergy.call("ping")""")

	def test_enqueue(self):
		# enqueue non whitelisted method
		self.assertRaises(
			finergy.PermissionError, safe_exec, """finergy.enqueue("finergy.get_user", now=True)"""
		)

		# enqueue whitelisted method
		safe_exec("""finergy.enqueue("ping", now=True)""")
