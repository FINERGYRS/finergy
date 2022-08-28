# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Reporting Solutions SAS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class UnhandledEmail(Document):
	pass


def remove_old_unhandled_emails():
	finergy.db.sql(
		"""DELETE FROM `tabUnhandled Email`
	WHERE creation < %s""",
		finergy.utils.add_days(finergy.utils.nowdate(), -30),
	)
