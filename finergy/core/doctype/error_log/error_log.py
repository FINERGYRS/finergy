# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class ErrorLog(Document):
	def onload(self):
		if not self.seen:
			self.db_set("seen", 1, update_modified=0)
			finergy.db.commit()


def set_old_logs_as_seen():
	# set logs as seen
	finergy.db.sql(
		"""UPDATE `tabError Log` SET `seen`=1
		WHERE `seen`=0 AND `creation` < (NOW() - INTERVAL '7' DAY)"""
	)


@finergy.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	finergy.only_for("System Manager")
	finergy.db.sql("""DELETE FROM `tabError Log`""")
