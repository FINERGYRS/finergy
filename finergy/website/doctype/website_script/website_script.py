# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class WebsiteScript(Document):
	def on_update(self):
		"""clear cache"""
		finergy.clear_cache(user="Guest")

		from finergy.website.render import clear_cache

		clear_cache()
