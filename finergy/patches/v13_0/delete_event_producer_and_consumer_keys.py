# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	if finergy.db.exists("DocType", "Event Producer"):
		finergy.db.sql("""UPDATE `tabEvent Producer` SET api_key='', api_secret=''""")
	if finergy.db.exists("DocType", "Event Consumer"):
		finergy.db.sql("""UPDATE `tabEvent Consumer` SET api_key='', api_secret=''""")
