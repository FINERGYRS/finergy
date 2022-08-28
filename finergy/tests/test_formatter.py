# -*- coding: utf-8 -*-
import unittest

import finergy
from finergy import format


class TestFormatter(unittest.TestCase):
	def test_currency_formatting(self):
		df = finergy._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = finergy._dict({"amount": 5})
		finergy.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		finergy.db.set_default("currency", None)
