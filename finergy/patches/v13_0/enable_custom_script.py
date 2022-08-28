# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	"""Enable all the existing Client script"""

	finergy.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
