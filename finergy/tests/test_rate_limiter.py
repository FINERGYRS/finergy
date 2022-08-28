#  -*- coding: utf-8 -*-

# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import time
import unittest

from werkzeug.wrappers import Response

import finergy
import finergy.rate_limiter
from finergy.rate_limiter import RateLimiter
from finergy.utils import cint


class TestRateLimiter(unittest.TestCase):
	def setUp(self):
		pass

	def test_apply_with_limit(self):
		finergy.conf.rate_limit = {"window": 86400, "limit": 1}
		finergy.rate_limiter.apply()

		self.assertTrue(hasattr(finergy.local, "rate_limiter"))
		self.assertIsInstance(finergy.local.rate_limiter, RateLimiter)

		finergy.cache().delete(finergy.local.rate_limiter.key)
		delattr(finergy.local, "rate_limiter")

	def test_apply_without_limit(self):
		finergy.conf.rate_limit = None
		finergy.rate_limiter.apply()

		self.assertFalse(hasattr(finergy.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		finergy.conf.rate_limit = {"window": 86400, "limit": 0.01}
		self.assertRaises(finergy.TooManyRequestsError, finergy.rate_limiter.apply)
		finergy.rate_limiter.update()

		response = finergy.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = finergy.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertNotIn("X-RateLimit-Used", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		finergy.cache().delete(limiter.key)
		finergy.cache().delete(finergy.local.rate_limiter.key)
		delattr(finergy.local, "rate_limiter")

	def test_respond_under_limit(self):
		finergy.conf.rate_limit = {"window": 86400, "limit": 0.01}
		finergy.rate_limiter.apply()
		finergy.rate_limiter.update()
		response = finergy.rate_limiter.respond()
		self.assertEqual(response, None)

		finergy.cache().delete(finergy.local.rate_limiter.key)
		delattr(finergy.local, "rate_limiter")

	def test_headers_under_limit(self):
		finergy.conf.rate_limit = {"window": 86400, "limit": 0.01}
		finergy.rate_limiter.apply()
		finergy.rate_limiter.update()
		headers = finergy.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Used"]), finergy.local.rate_limiter.duration)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 10000)

		finergy.cache().delete(finergy.local.rate_limiter.key)
		delattr(finergy.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(finergy.TooManyRequestsError, limiter.apply)

		finergy.cache().delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		finergy.cache().delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(finergy.cache().get(limiter.key)))

		finergy.cache().delete(limiter.key)
