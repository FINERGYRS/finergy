# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import unittest

import finergy
from finergy.utils import set_request
from finergy.website.render import render

test_dependencies = ["Blog Post"]


class TestWebsiteRouteMeta(unittest.TestCase):
	def test_meta_tag_generation(self):
		blogs = finergy.get_all(
			"Blog Post", fields=["name", "route"], filters={"published": 1, "route": ("!=", "")}, limit=1
		)

		blog = blogs[0]

		# create meta tags for this route
		doc = finergy.new_doc("Website Route Meta")
		doc.append("meta_tags", {"key": "type", "value": "blog_post"})
		doc.append("meta_tags", {"key": "og:title", "value": "My Blog"})
		doc.name = blog.route
		doc.insert()

		# set request on this route
		set_request(path=blog.route)
		response = render()

		self.assertTrue(response.status_code, 200)

		html = response.get_data().decode()

		self.assertTrue("""<meta name="type" content="blog_post">""" in html)
		self.assertTrue("""<meta property="og:title" content="My Blog">""" in html)

	def tearDown(self):
		finergy.db.rollback()
