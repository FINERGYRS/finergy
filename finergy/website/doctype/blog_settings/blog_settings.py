# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class BlogSettings(Document):
	def on_update(self):
		from finergy.website.render import clear_cache

		clear_cache("blog")
		clear_cache("writers")


def get_feedback_limit():
	return finergy.db.get_single_value("Blog Settings", "feedback_limit") or 0
