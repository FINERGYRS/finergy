# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class HasRole(Document):
	def before_insert(self):
		if finergy.db.exists("Has Role", {"parent": self.parent, "role": self.role}):
			finergy.throw(finergy._("User '{0}' already has the role '{1}'").format(self.parent, self.role))
