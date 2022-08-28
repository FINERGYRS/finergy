# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("email", "doctype", "Newsletter")
	finergy.db.sql(
		"""
		UPDATE tabNewsletter
		SET content_type = 'Rich Text'
	"""
	)
