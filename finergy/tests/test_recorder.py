#  -*- coding: utf-8 -*-

# Copyright (c) 2019, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import unittest

import sqlparse

import finergy
import finergy.recorder
from finergy.utils import set_request
from finergy.website.render import render_page


class TestRecorder(unittest.TestCase):
	def setUp(self):
		finergy.recorder.stop()
		finergy.recorder.delete()
		set_request()
		finergy.recorder.start()
		finergy.recorder.record()

	def test_start(self):
		finergy.recorder.dump()
		requests = finergy.recorder.get()
		self.assertEqual(len(requests), 1)

	def test_do_not_record(self):
		finergy.recorder.do_not_record(finergy.get_all)("DocType")
		finergy.recorder.dump()
		requests = finergy.recorder.get()
		self.assertEqual(len(requests), 0)

	def test_get(self):
		finergy.recorder.dump()

		requests = finergy.recorder.get()
		self.assertEqual(len(requests), 1)

		request = finergy.recorder.get(requests[0]["uuid"])
		self.assertTrue(request)

	def test_delete(self):
		finergy.recorder.dump()

		requests = finergy.recorder.get()
		self.assertEqual(len(requests), 1)

		finergy.recorder.delete()

		requests = finergy.recorder.get()
		self.assertEqual(len(requests), 0)

	def test_record_without_sql_queries(self):
		finergy.recorder.dump()

		requests = finergy.recorder.get()
		request = finergy.recorder.get(requests[0]["uuid"])

		self.assertEqual(len(request["calls"]), 0)

	def test_record_with_sql_queries(self):
		finergy.get_all("DocType")
		finergy.recorder.dump()

		requests = finergy.recorder.get()
		request = finergy.recorder.get(requests[0]["uuid"])

		self.assertNotEqual(len(request["calls"]), 0)

	def test_explain(self):
		finergy.db.sql("SELECT * FROM tabDocType")
		finergy.db.sql("COMMIT")
		finergy.recorder.dump()

		requests = finergy.recorder.get()
		request = finergy.recorder.get(requests[0]["uuid"])

		self.assertEqual(len(request["calls"][0]["explain_result"]), 1)
		self.assertEqual(len(request["calls"][1]["explain_result"]), 0)

	def test_multiple_queries(self):
		queries = [
			{"mariadb": "SELECT * FROM tabDocType", "postgres": 'SELECT * FROM "tabDocType"'},
			{"mariadb": "SELECT COUNT(*) FROM tabDocType", "postgres": 'SELECT COUNT(*) FROM "tabDocType"'},
			{"mariadb": "COMMIT", "postgres": "COMMIT"},
		]

		sql_dialect = finergy.db.db_type or "mariadb"
		for query in queries:
			finergy.db.sql(query[sql_dialect])

		finergy.recorder.dump()

		requests = finergy.recorder.get()
		request = finergy.recorder.get(requests[0]["uuid"])

		self.assertEqual(len(request["calls"]), len(queries))

		for query, call in zip(queries, request["calls"]):
			self.assertEqual(
				call["query"], sqlparse.format(query[sql_dialect].strip(), keyword_case="upper", reindent=True)
			)

	def test_duplicate_queries(self):
		queries = [
			("SELECT * FROM tabDocType", 2),
			("SELECT COUNT(*) FROM tabDocType", 1),
			("select * from tabDocType", 2),
			("COMMIT", 3),
			("COMMIT", 3),
			("COMMIT", 3),
		]
		for query in queries:
			finergy.db.sql(query[0])

		finergy.recorder.dump()

		requests = finergy.recorder.get()
		request = finergy.recorder.get(requests[0]["uuid"])

		for query, call in zip(queries, request["calls"]):
			self.assertEqual(call["exact_copies"], query[1])

	def test_error_page_rendering(self):
		content = render_page("error")
		self.assertIn("Error", content)
