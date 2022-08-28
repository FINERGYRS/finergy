# Copyright (c) 2018, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
