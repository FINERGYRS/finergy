# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.model.document import Document


class ClientScript(Document):
	def autoname(self):
		self.name = f"{self.dt}-{self.view}"

	def validate(self):
		if not self.is_new():
			return

		exists = finergy.db.exists("Client Script", {"dt": self.dt, "view": self.view})
		if exists:
			finergy.throw(
				_("Client Script for {0} {1} already exists").format(finergy.bold(self.dt), self.view),
				finergy.DuplicateEntryError,
			)

	def on_update(self):
		finergy.clear_cache(doctype=self.dt)

	def on_trash(self):
		finergy.clear_cache(doctype=self.dt)
