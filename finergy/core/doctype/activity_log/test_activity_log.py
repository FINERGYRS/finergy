# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import time
import unittest

import finergy
from finergy.auth import CookieManager, LoginManager


class TestActivityLog(unittest.TestCase):
	def test_activity_log(self):

		# test user login log
		finergy.local.form_dict = finergy._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": finergy.conf.admin_password or "admin",
				"usr": "Administrator",
			}
		)

		finergy.local.cookie_manager = CookieManager()
		finergy.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(finergy.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		finergy.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		finergy.form_dict.update({"pwd": "password"})
		self.assertRaises(finergy.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		finergy.local.form_dict = finergy._dict()

	def get_auth_log(self, operation="Login"):
		names = finergy.db.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		auth_log = finergy.get_doc("Activity Log", name)
		return auth_log

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		finergy.local.form_dict = finergy._dict(
			{"cmd": "login", "sid": "Guest", "pwd": "admin", "usr": "Administrator"}
		)

		finergy.local.cookie_manager = CookieManager()
		finergy.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEquals(auth_log.status, "Success")

		# test user logout log
		finergy.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEquals(auth_log.status, "Success")

		# test invalid login
		finergy.form_dict.update({"pwd": "password"})
		self.assertRaises(finergy.AuthenticationError, LoginManager)
		self.assertRaises(finergy.AuthenticationError, LoginManager)
		self.assertRaises(finergy.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(finergy.AuthenticationError, LoginManager)
		self.assertRaises(finergy.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(finergy.AuthenticationError, LoginManager)

		finergy.local.form_dict = finergy._dict()


def update_system_settings(args):
	doc = finergy.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
