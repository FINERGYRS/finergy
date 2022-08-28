# -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import finergy
from finergy.model.document import Document
from finergy.utils.safe_exec import safe_exec


class SystemConsole(Document):
	def run(self):
		finergy.only_for("System Manager")
		try:
			finergy.debug_log = []
			safe_exec(self.console)
			self.output = "\n".join(finergy.debug_log)
		except Exception:
			self.output = finergy.get_traceback()

		if self.commit:
			finergy.db.commit()
		else:
			finergy.db.rollback()

		finergy.get_doc(dict(doctype="Console Log", script=self.console, output=self.output)).insert()
		finergy.db.commit()


@finergy.whitelist()
def execute_code(doc):
	console = finergy.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()
