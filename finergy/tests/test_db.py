#  -*- coding: utf-8 -*-

# Copyright (c) 2022, Finergy Reporting Solutions SAS and Contributors
# License: MIT. See LICENSE

from __future__ import unicode_literals

import datetime
import inspect
import unittest
from random import choice
from unittest.mock import patch

import finergy
from finergy.custom.doctype.custom_field.custom_field import create_custom_field
from finergy.database.database import Database
from finergy.tests.test_query_builder import db_type_is, run_only_if
from finergy.utils import add_days, cint, now, random_string
from finergy.utils.testutils import clear_custom_fields


class TestDB(unittest.TestCase):
	def test_get_value(self):
		self.assertEqual(finergy.db.get_value("User", {"name": ["=", "Administrator"]}), "Administrator")
		self.assertEqual(finergy.db.get_value("User", {"name": ["like", "Admin%"]}), "Administrator")
		self.assertNotEquals(finergy.db.get_value("User", {"name": ["!=", "Guest"]}), "Guest")
		self.assertEqual(finergy.db.get_value("User", {"name": ["<", "Adn"]}), "Administrator")
		self.assertEqual(finergy.db.get_value("User", {"name": ["<=", "Administrator"]}), "Administrator")

		self.assertEqual(
			finergy.db.sql("""SELECT name FROM `tabUser` WHERE name > 's' ORDER BY MODIFIED DESC""")[0][0],
			finergy.db.get_value("User", {"name": [">", "s"]}),
		)

		self.assertEqual(
			finergy.db.sql("""SELECT name FROM `tabUser` WHERE name >= 't' ORDER BY MODIFIED DESC""")[0][0],
			finergy.db.get_value("User", {"name": [">=", "t"]}),
		)

	def test_get_value_limits(self):

		filters = {"enabled": 1}

		self.assertEqual(1, len(finergy.db.get_values("User", filters=filters, limit=1)))
		# count of last touched rows as per DB-API 2.0 https://peps.python.org/pep-0249/#rowcount
		self.assertGreaterEqual(1, cint(finergy.db._cursor.rowcount))
		self.assertEqual(2, len(finergy.db.get_values("User", filters=filters, limit=2)))
		self.assertGreaterEqual(2, cint(finergy.db._cursor.rowcount))

		# without limits length == count
		self.assertEqual(
			len(finergy.db.get_values("User", filters=filters)), finergy.db.count("User", filters)
		)

		finergy.db.get_value("User", filters=filters)
		self.assertGreaterEqual(1, cint(finergy.db._cursor.rowcount))

		finergy.db.exists("User", filters)
		self.assertGreaterEqual(1, cint(finergy.db._cursor.rowcount))

	def test_escape(self):
		finergy.db.escape("香港濟生堂製藥有限公司 - IT".encode("utf-8"))

	def test_get_single_value(self):
		# setup
		values_dict = {
			"Float": 1.5,
			"Int": 1,
			"Percent": 55.5,
			"Currency": 12.5,
			"Data": "Test",
			"Date": datetime.datetime.now().date(),
			"Datetime": datetime.datetime.now(),
			"Time": datetime.timedelta(hours=9, minutes=45, seconds=10),
		}
		test_inputs = [
			{"fieldtype": fieldtype, "value": value} for fieldtype, value in values_dict.items()
		]
		for fieldtype in values_dict.keys():
			create_custom_field(
				"Print Settings",
				{
					"fieldname": f"test_{fieldtype.lower()}",
					"label": f"Test {fieldtype}",
					"fieldtype": fieldtype,
				},
			)

		# test
		for inp in test_inputs:
			fieldname = f"test_{inp['fieldtype'].lower()}"
			finergy.db.set_value("Print Settings", "Print Settings", fieldname, inp["value"])
			self.assertEqual(finergy.db.get_single_value("Print Settings", fieldname), inp["value"])

		# teardown
		clear_custom_fields("Print Settings")

	def test_log_touched_tables(self):
		finergy.flags.in_migrate = True
		finergy.flags.touched_tables = set()
		finergy.db.set_value("System Settings", "System Settings", "backup_limit", 5)
		self.assertIn("tabSingles", finergy.flags.touched_tables)

		finergy.flags.touched_tables = set()
		todo = finergy.get_doc({"doctype": "ToDo", "description": "Random Description"})
		todo.save()
		self.assertIn("tabToDo", finergy.flags.touched_tables)

		finergy.flags.touched_tables = set()
		todo.description = "Another Description"
		todo.save()
		self.assertIn("tabToDo", finergy.flags.touched_tables)

		if finergy.db.db_type != "postgres":
			finergy.flags.touched_tables = set()
			finergy.db.sql("UPDATE tabToDo SET description = 'Updated Description'")
			self.assertNotIn("tabToDo SET", finergy.flags.touched_tables)
			self.assertIn("tabToDo", finergy.flags.touched_tables)

		finergy.flags.touched_tables = set()
		todo.delete()
		self.assertIn("tabToDo", finergy.flags.touched_tables)

		finergy.flags.touched_tables = set()
		create_custom_field("ToDo", {"label": "ToDo Custom Field"})

		self.assertIn("tabToDo", finergy.flags.touched_tables)
		self.assertIn("tabCustom Field", finergy.flags.touched_tables)
		finergy.flags.in_migrate = False
		finergy.flags.touched_tables.clear()

	def test_db_keywords_as_fields(self):
		"""Tests if DB keywords work as docfield names. If they're wrapped with grave accents."""
		# Using random.choices, picked out a list of 40 keywords for testing
		all_keywords = {
			"mariadb": [
				"CHARACTER",
				"DELAYED",
				"LINES",
				"EXISTS",
				"YEAR_MONTH",
				"LOCALTIME",
				"BOTH",
				"MEDIUMINT",
				"LEFT",
				"BINARY",
				"DEFAULT",
				"KILL",
				"WRITE",
				"SQL_SMALL_RESULT",
				"CURRENT_TIME",
				"CROSS",
				"INHERITS",
				"SELECT",
				"TABLE",
				"ALTER",
				"CURRENT_TIMESTAMP",
				"XOR",
				"CASE",
				"ALL",
				"WHERE",
				"INT",
				"TO",
				"SOME",
				"DAY_MINUTE",
				"ERRORS",
				"OPTIMIZE",
				"REPLACE",
				"HIGH_PRIORITY",
				"VARBINARY",
				"HELP",
				"IS",
				"CHAR",
				"DESCRIBE",
				"KEY",
			],
			"postgres": [
				"WORK",
				"LANCOMPILER",
				"REAL",
				"HAVING",
				"REPEATABLE",
				"DATA",
				"USING",
				"BIT",
				"DEALLOCATE",
				"SERIALIZABLE",
				"CURSOR",
				"INHERITS",
				"ARRAY",
				"TRUE",
				"IGNORE",
				"PARAMETER_MODE",
				"ROW",
				"CHECKPOINT",
				"SHOW",
				"BY",
				"SIZE",
				"SCALE",
				"UNENCRYPTED",
				"WITH",
				"AND",
				"CONVERT",
				"FIRST",
				"SCOPE",
				"WRITE",
				"INTERVAL",
				"CHARACTER_SET_SCHEMA",
				"ADD",
				"SCROLL",
				"NULL",
				"WHEN",
				"TRANSACTION_ACTIVE",
				"INT",
				"FORTRAN",
				"STABLE",
			],
		}
		created_docs = []

		# edit by rushabh: added [:1]
		# don't run every keyword! - if one works, they all do
		fields = all_keywords[finergy.conf.db_type][:1]
		test_doctype = "ToDo"

		def add_custom_field(field):
			create_custom_field(
				test_doctype,
				{
					"fieldname": field.lower(),
					"label": field.title(),
					"fieldtype": "Data",
				},
			)

		# Create custom fields for test_doctype
		for field in fields:
			add_custom_field(field)

		# Create documents under that doctype and query them via ORM
		for _ in range(10):
			docfields = {key.lower(): random_string(10) for key in fields}
			doc = finergy.get_doc({"doctype": test_doctype, "description": random_string(20), **docfields})
			doc.insert()
			created_docs.append(doc.name)

		random_field = choice(fields).lower()
		random_doc = choice(created_docs)
		random_value = random_string(20)

		# Testing read
		self.assertEqual(
			list(finergy.get_all("ToDo", fields=[random_field], limit=1)[0])[0], random_field
		)
		self.assertEqual(
			list(finergy.get_all("ToDo", fields=[f"`{random_field}` as total"], limit=1)[0])[0], "total"
		)

		# Testing read for distinct and sql functions
		self.assertEqual(
			list(
				finergy.get_all(
					"ToDo",
					fields=[f"`{random_field}` as total"],
					distinct=True,
					limit=1,
				)[0]
			)[0],
			"total",
		)
		self.assertEqual(
			list(
				finergy.get_all(
					"ToDo",
					fields=[f"`{random_field}`"],
					distinct=True,
					limit=1,
				)[0]
			)[0],
			random_field,
		)
		self.assertEqual(
			list(finergy.get_all("ToDo", fields=[f"count(`{random_field}`)"], limit=1)[0])[0],
			"count" if finergy.conf.db_type == "postgres" else f"count(`{random_field}`)",
		)

		# Testing update
		finergy.db.set_value(test_doctype, random_doc, random_field, random_value)
		self.assertEqual(finergy.db.get_value(test_doctype, random_doc, random_field), random_value)

		# Cleanup - delete records and remove custom fields
		for doc in created_docs:
			finergy.delete_doc(test_doctype, doc)
		clear_custom_fields(test_doctype)

	def test_savepoints(self):
		finergy.db.rollback()
		save_point = "todonope"

		created_docs = []
		failed_docs = []

		for _ in range(5):
			finergy.db.savepoint(save_point)
			doc_gone = finergy.get_doc(doctype="ToDo", description="nope").save()
			failed_docs.append(doc_gone.name)
			finergy.db.rollback(save_point=save_point)
			doc_kept = finergy.get_doc(doctype="ToDo", description="nope").save()
			created_docs.append(doc_kept.name)
		finergy.db.commit()

		for d in failed_docs:
			self.assertFalse(finergy.db.exists("ToDo", d))
		for d in created_docs:
			self.assertTrue(finergy.db.exists("ToDo", d))

	@run_only_if(db_type_is.MARIADB)
	def test_transaction_writes_error(self):
		from finergy.database.database import Database

		finergy.db.rollback()

		finergy.db.MAX_WRITES_PER_TRANSACTION = 1
		note = finergy.get_last_doc("ToDo")
		note.description = "changed"
		with self.assertRaises(finergy.TooManyWritesError) as tmw:
			note.save()

		finergy.db.MAX_WRITES_PER_TRANSACTION = Database.MAX_WRITES_PER_TRANSACTION


@run_only_if(db_type_is.MARIADB)
class TestDDLCommandsMaria(unittest.TestCase):
	test_table_name = "TestNotes"

	def setUp(self) -> None:
		finergy.db.commit()
		finergy.db.sql(
			f"""
			CREATE TABLE `tab{self.test_table_name}` (`id` INT NULL,PRIMARY KEY (`id`));
			"""
		)

	def tearDown(self) -> None:
		finergy.db.sql(f"DROP TABLE tab{self.test_table_name};")
		self.test_table_name = "TestNotes"

	def test_rename(self) -> None:
		new_table_name = f"{self.test_table_name}_new"
		finergy.db.rename_table(self.test_table_name, new_table_name)
		check_exists = finergy.db.sql(
			f"""
			SELECT * FROM INFORMATION_SCHEMA.TABLES
			WHERE TABLE_NAME = N'tab{new_table_name}';
			"""
		)
		self.assertGreater(len(check_exists), 0)
		self.assertIn(f"tab{new_table_name}", check_exists[0])

		# * so this table is deleted after the rename
		self.test_table_name = new_table_name

	def test_describe(self) -> None:
		self.assertEqual(
			(("id", "int(11)", "NO", "PRI", None, ""),),
			finergy.db.describe(self.test_table_name),
		)

	def test_change_type(self) -> None:
		finergy.db.change_column_type("TestNotes", "id", "varchar(255)")
		test_table_description = finergy.db.sql(f"DESC tab{self.test_table_name};")
		self.assertGreater(len(test_table_description), 0)
		self.assertIn("varchar(255)", test_table_description[0])


class TestDBSetValue(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.todo1 = finergy.get_doc(doctype="ToDo", description="test_set_value 1").insert()
		cls.todo2 = finergy.get_doc(doctype="ToDo", description="test_set_value 2").insert()

	def test_update_single_doctype_field(self):
		value = finergy.db.get_single_value("System Settings", "deny_multiple_sessions")
		changed_value = not value

		finergy.db.set_value(
			"System Settings", "System Settings", "deny_multiple_sessions", changed_value
		)
		current_value = finergy.db.get_single_value("System Settings", "deny_multiple_sessions")
		self.assertEqual(current_value, changed_value)

		changed_value = not current_value
		finergy.db.set_value("System Settings", None, "deny_multiple_sessions", changed_value)
		current_value = finergy.db.get_single_value("System Settings", "deny_multiple_sessions")
		self.assertEqual(current_value, changed_value)

		changed_value = not current_value
		finergy.db.set_single_value("System Settings", "deny_multiple_sessions", changed_value)
		current_value = finergy.db.get_single_value("System Settings", "deny_multiple_sessions")
		self.assertEqual(current_value, changed_value)

	def test_update_single_row_single_column(self):
		finergy.db.set_value("ToDo", self.todo1.name, "description", "test_set_value change 1")
		updated_value = finergy.db.get_value("ToDo", self.todo1.name, "description")
		self.assertEqual(updated_value, "test_set_value change 1")

	def test_update_single_row_multiple_columns(self):
		description, status = "Upated by test_update_single_row_multiple_columns", "Closed"

		finergy.db.set_value(
			"ToDo",
			self.todo1.name,
			{
				"description": description,
				"status": status,
			},
			update_modified=False,
		)

		updated_desciption, updated_status = finergy.db.get_value(
			"ToDo", filters={"name": self.todo1.name}, fieldname=["description", "status"]
		)

		self.assertEqual(description, updated_desciption)
		self.assertEqual(status, updated_status)

	def test_update_multiple_rows_single_column(self):
		finergy.db.set_value(
			"ToDo", {"description": ("like", "%test_set_value%")}, "description", "change 2"
		)

		self.assertEqual(finergy.db.get_value("ToDo", self.todo1.name, "description"), "change 2")
		self.assertEqual(finergy.db.get_value("ToDo", self.todo2.name, "description"), "change 2")

	def test_update_multiple_rows_multiple_columns(self):
		todos_to_update = finergy.get_all(
			"ToDo",
			filters={"description": ("like", "%test_set_value%"), "status": ("!=", "Closed")},
			pluck="name",
		)

		finergy.db.set_value(
			"ToDo",
			{"description": ("like", "%test_set_value%"), "status": ("!=", "Closed")},
			{"status": "Closed", "priority": "High"},
		)

		test_result = finergy.get_all(
			"ToDo", filters={"name": ("in", todos_to_update)}, fields=["status", "priority"]
		)

		self.assertTrue(all(x for x in test_result if x["status"] == "Closed"))
		self.assertTrue(all(x for x in test_result if x["priority"] == "High"))

	def test_update_modified_options(self):
		self.todo2.reload()

		todo = self.todo2
		updated_description = f"{todo.description} - by `test_update_modified_options`"
		custom_modified = datetime.datetime.fromisoformat(add_days(now(), 10))
		custom_modified_by = "user_that_doesnt_exist@example.com"

		finergy.db.set_value("ToDo", todo.name, "description", updated_description, update_modified=False)
		self.assertEqual(updated_description, finergy.db.get_value("ToDo", todo.name, "description"))
		self.assertEqual(todo.modified, finergy.db.get_value("ToDo", todo.name, "modified"))

		finergy.db.set_value(
			"ToDo",
			todo.name,
			"description",
			"test_set_value change 1",
			modified=custom_modified,
			modified_by=custom_modified_by,
		)
		self.assertTupleEqual(
			(custom_modified, custom_modified_by),
			finergy.db.get_value("ToDo", todo.name, ["modified", "modified_by"]),
		)

	def test_for_update(self):
		self.todo1.reload()

		with patch.object(Database, "sql") as sql_called:
			finergy.db.set_value(
				self.todo1.doctype,
				self.todo1.name,
				"description",
				f"{self.todo1.description}-edit by `test_for_update`",
			)
			first_query = sql_called.call_args_list[0][0][0]
			second_query = sql_called.call_args_list[1][0][0]

			self.assertTrue(sql_called.call_count == 2)
			self.assertTrue("FOR UPDATE".casefold() in first_query)
			if finergy.conf.db_type == "postgres":
				from finergy.database.postgres.database import modify_query

				self.assertTrue(modify_query("UPDATE `tabToDo` SET") in second_query)
			if finergy.conf.db_type == "mariadb":
				self.assertTrue("UPDATE `tabToDo` SET" in second_query)

	def test_cleared_cache(self):
		self.todo2.reload()

		with patch.object(finergy, "clear_document_cache") as clear_cache:
			finergy.db.set_value(
				self.todo2.doctype,
				self.todo2.name,
				"description",
				f"{self.todo2.description}-edit by `test_cleared_cache`",
			)
			clear_cache.assert_called()

	def test_update_alias(self):
		args = (self.todo1.doctype, self.todo1.name, "description", "Updated by `test_update_alias`")
		kwargs = {
			"for_update": False,
			"modified": None,
			"modified_by": None,
			"update_modified": True,
			"debug": False,
		}

		self.assertTrue("return self.set_value(" in inspect.getsource(finergy.db.update))

		with patch.object(Database, "set_value") as set_value:
			finergy.db.update(*args, **kwargs)
			set_value.assert_called_once()
			set_value.assert_called_with(*args, **kwargs)

	@classmethod
	def tearDownClass(cls):
		finergy.db.rollback()


@run_only_if(db_type_is.POSTGRES)
class TestDDLCommandsPost(unittest.TestCase):
	test_table_name = "TestNotes"

	def setUp(self) -> None:
		finergy.db.sql(
			f"""
			CREATE TABLE "tab{self.test_table_name}" ("id" INT NULL,PRIMARY KEY ("id"))
			"""
		)

	def tearDown(self) -> None:
		finergy.db.sql(f'DROP TABLE "tab{self.test_table_name}"')
		self.test_table_name = "TestNotes"

	def test_rename(self) -> None:
		new_table_name = f"{self.test_table_name}_new"
		finergy.db.rename_table(self.test_table_name, new_table_name)
		check_exists = finergy.db.sql(
			f"""
			SELECT EXISTS (
			SELECT FROM information_schema.tables
			WHERE  table_name = 'tab{new_table_name}'
			);
			"""
		)
		self.assertTrue(check_exists[0][0])

		# * so this table is deleted after the rename
		self.test_table_name = new_table_name

	def test_describe(self) -> None:
		self.assertEqual([("id",)], finergy.db.describe(self.test_table_name))

	def test_change_type(self) -> None:
		finergy.db.change_column_type(self.test_table_name, "id", "varchar(255)")
		check_change = finergy.db.sql(
			f"""
			SELECT
				table_name,
				column_name,
				data_type
			FROM
				information_schema.columns
			WHERE
				table_name = 'tab{self.test_table_name}'
			"""
		)
		self.assertGreater(len(check_change), 0)
		self.assertIn("character varying", check_change[0])
