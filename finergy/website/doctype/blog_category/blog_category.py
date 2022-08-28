# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from finergy.website.render import clear_cache
from finergy.website.website_generator import WebsiteGenerator


class BlogCategory(WebsiteGenerator):
	def autoname(self):
		# to override autoname of WebsiteGenerator
		self.name = self.scrub(self.title)

	def on_update(self):
		clear_cache()

	def set_route(self):
		# Override blog route since it has to been templated
		self.route = "blog/" + self.name
