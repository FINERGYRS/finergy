# -*- coding: utf-8 -*-
# Copyright (c) 2017, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class PrintStyle(Document):
	def validate(self):
		if (
			self.standard == 1
			and not finergy.local.conf.get("developer_mode")
			and not (finergy.flags.in_import or finergy.flags.in_test)
		):

			finergy.throw(finergy._("Standard Print Style cannot be changed. Please duplicate to edit."))

	def on_update(self):
		self.export_doc()

	def export_doc(self):
		# export
		from finergy.modules.utils import export_module_json

		export_module_json(self, self.standard == 1, "Printing")
