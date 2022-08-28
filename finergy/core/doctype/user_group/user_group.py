# -*- coding: utf-8 -*-
# Copyright (c) 2021, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy

# import finergy
from finergy.model.document import Document


class UserGroup(Document):
	def after_insert(self):
		finergy.cache().delete_key("user_groups")

	def on_trash(self):
		finergy.cache().delete_key("user_groups")
