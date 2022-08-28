# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors

from __future__ import unicode_literals

import unittest

import finergy


class TestClient(unittest.TestCase):
	def test_set_value(self):
		todo = finergy.get_doc(dict(doctype="ToDo", description="test")).insert()
		finergy.set_value("ToDo", todo.name, "description", "test 1")
		self.assertEqual(finergy.get_value("ToDo", todo.name, "description"), "test 1")

		finergy.set_value("ToDo", todo.name, {"description": "test 2"})
		self.assertEqual(finergy.get_value("ToDo", todo.name, "description"), "test 2")

	def test_delete(self):
		from finergy.client import delete

		todo = finergy.get_doc(dict(doctype="ToDo", description="description")).insert()
		delete("ToDo", todo.name)

		self.assertFalse(finergy.db.exists("ToDo", todo.name))
		self.assertRaises(finergy.DoesNotExistError, delete, "ToDo", todo.name)

	def test_http_valid_method_access(self):
		from finergy.client import delete
		from finergy.handler import execute_cmd

		finergy.set_user("Administrator")

		finergy.local.request = finergy._dict()
		finergy.local.request.method = "POST"

		finergy.local.form_dict = finergy._dict(
			{"doc": dict(doctype="ToDo", description="Valid http method"), "cmd": "finergy.client.save"}
		)
		todo = execute_cmd("finergy.client.save")

		self.assertEqual(todo.get("description"), "Valid http method")

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from finergy.handler import execute_cmd

		finergy.set_user("Administrator")

		finergy.local.request = finergy._dict()
		finergy.local.request.method = "GET"

		finergy.local.form_dict = finergy._dict(
			{"doc": dict(doctype="ToDo", description="Invalid http method"), "cmd": "finergy.client.save"}
		)

		self.assertRaises(finergy.PermissionError, execute_cmd, "finergy.client.save")

	def test_run_doc_method(self):
		from finergy.handler import execute_cmd

		if not finergy.db.exists("Report", "Test Run Doc Method"):
			report = finergy.get_doc(
				{
					"doctype": "Report",
					"ref_doctype": "User",
					"report_name": "Test Run Doc Method",
					"report_type": "Query Report",
					"is_standard": "No",
					"roles": [{"role": "System Manager"}],
				}
			).insert()
		else:
			report = finergy.get_doc("Report", "Test Run Doc Method")

		finergy.local.request = finergy._dict()
		finergy.local.request.method = "GET"

		# Whitelisted, works as expected
		finergy.local.form_dict = finergy._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "toggle_disable",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		execute_cmd(finergy.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		finergy.local.form_dict = finergy._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "create_report_py",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		self.assertRaises(finergy.PermissionError, execute_cmd, finergy.local.form_dict.cmd)

	def test_client_get(self):
		from finergy.client import get

		todo = finergy.get_doc(doctype="ToDo", description="test").insert()
		filters = {"name": todo.name}
		filters_json = finergy.as_json(filters)

		self.assertEqual(get("ToDo", filters=filters).description, "test")
		self.assertEqual(get("ToDo", filters=filters_json).description, "test")
		self.assertEqual(get("System Settings", "", "").doctype, "System Settings")
		self.assertEqual(get("ToDo", filters={}), get("ToDo", filters="{}"))
		todo.delete()
