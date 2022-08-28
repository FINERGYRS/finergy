# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# See license.txt

from __future__ import unicode_literals

import os
import unittest

import finergy

from .website_theme import get_scss_paths


class TestWebsiteTheme(unittest.TestCase):
	def test_website_theme(self):
		finergy.delete_doc_if_exists("Website Theme", "test-theme")
		theme = finergy.get_doc(
			dict(
				doctype="Website Theme",
				theme="test-theme",
				google_font="Inter",
				custom_scss="body { font-size: 16.5px; }",  # this will get minified!
			)
		).insert()

		theme_path = finergy.get_site_path("public", theme.theme_url[1:])
		with open(theme_path) as theme_file:
			css = theme_file.read()

		self.assertTrue("body{font-size:16.5px}" in css)
		self.assertTrue("fonts.googleapis.com" in css)

	def test_get_scss_paths(self):
		self.assertIn("finergy/public/scss/website", get_scss_paths())

	def test_imports_to_ignore(self):
		finergy.delete_doc_if_exists("Website Theme", "test-theme")
		theme = finergy.get_doc(
			dict(doctype="Website Theme", theme="test-theme", ignored_apps=[{"app": "finergy"}])
		).insert()

		self.assertTrue('@import "finergy/public/scss/website"' not in theme.theme_scss)
