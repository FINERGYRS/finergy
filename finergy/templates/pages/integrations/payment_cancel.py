# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# See license.txt

from __future__ import unicode_literals

import finergy


def get_context(context):
	token = finergy.local.form_dict.token

	if token:
		finergy.db.set_value("Integration Request", token, "status", "Cancelled")
		finergy.db.commit()
