#  -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import unittest

import finergy
import finergy.monitor
from finergy.monitor import MONITOR_REDIS_KEY
from finergy.utils import set_request
from finergy.utils.response import build_response


class TestMonitor(unittest.TestCase):
	def setUp(self):
		finergy.conf.monitor = 1
		finergy.cache().delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/finergy.ping")
		response = build_response("json")

		finergy.monitor.start()
		finergy.monitor.stop(response)

		logs = finergy.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = finergy.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		finergy.utils.background_jobs.execute_job(
			finergy.local.site, "finergy.ping", None, None, {}, is_async=False
		)

		logs = finergy.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = finergy.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "finergy.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/finergy.ping")
		response = build_response("json")
		finergy.monitor.start()
		finergy.monitor.stop(response)

		open(finergy.monitor.log_file(), "w").close()
		finergy.monitor.flush()

		with open(finergy.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = finergy.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def tearDown(self):
		finergy.conf.monitor = 0
		finergy.cache().delete_value(MONITOR_REDIS_KEY)
