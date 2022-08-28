# -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy


class TestSystemConsole(unittest.TestCase):
	def test_system_console(self):
		system_console = finergy.get_doc("System Console")
		system_console.console = 'log("hello")'
		system_console.run()

		self.assertEqual(system_console.output, "hello")

		system_console.console = 'log(finergy.db.get_value("DocType", "DocType", "module"))'
		system_console.run()

		self.assertEqual(system_console.output, "Core")
