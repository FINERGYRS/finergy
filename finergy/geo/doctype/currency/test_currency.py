# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# License: See license.txt

# pre loaded

from __future__ import unicode_literals

import finergy
from finergy.tests.utils import FinergyTestCase


class TestUser(FinergyTestCase):
	def test_default_currency_on_setup(self):
		usd = finergy.get_doc("Currency", "USD")
		self.assertTrue(usd.enabled)
		self.assertEqual(usd.fraction, "Cent")
