# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.model.document import Document
from finergy.utils import cint


class PrintSettings(Document):
	def validate(self):
		if self.pdf_page_size == "Custom" and not (self.pdf_page_height and self.pdf_page_width):
			finergy.throw(_("Page height and width cannot be zero"))

	def on_update(self):
		finergy.clear_cache()


@finergy.whitelist()
def is_print_server_enabled():
	if not hasattr(finergy.local, "enable_print_server"):
		finergy.local.enable_print_server = cint(
			finergy.db.get_single_value("Print Settings", "enable_print_server")
		)

	return finergy.local.enable_print_server
