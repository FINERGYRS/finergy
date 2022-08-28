# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import os
import unittest

import finergy
import finergy.translate

# class TestTranslations(unittest.TestCase):
# 	def test_doctype(self, messages=None):
# 		if not messages:
# 			messages = finergy.translate.get_messages_from_doctype("Role")
# 		self.assertTrue("Role Name" in messages)
#
# 	def test_page(self, messages=None):
# 		if not messages:
# 			messages = finergy.translate.get_messages_from_page("finder")
# 		self.assertTrue("Finder" in messages)
#
# 	def test_report(self, messages=None):
# 		if not messages:
# 			messages = finergy.translate.get_messages_from_report("ToDo")
# 		self.assertTrue("Test" in messages)
#
# 	def test_include_js(self, messages=None):
# 		if not messages:
# 			messages = finergy.translate.get_messages_from_include_files("finergy")
# 		self.assertTrue("History" in messages)
#
# 	def test_server(self, messages=None):
# 		if not messages:
# 			messages = finergy.translate.get_server_messages("finergy")
# 		self.assertTrue("Login" in messages)
# 		self.assertTrue("Did not save" in messages)
#
# 	def test_all_app(self):
# 		messages = finergy.translate.get_messages_for_app("finergy")
# 		self.test_doctype(messages)
# 		self.test_page(messages)
# 		self.test_report(messages)
# 		self.test_include_js(messages)
# 		self.test_server(messages)
#
# 	def test_load_translations(self):
# 		finergy.translate.clear_cache()
# 		self.assertFalse(finergy.cache().hget("lang_full_dict", "de"))
#
# 		langdict = finergy.translate.get_full_dict("de")
# 		self.assertEqual(langdict['Row'], 'Reihe')
#
# 	def test_write_csv(self):
# 		tpath = finergy.get_pymodule_path("finergy", "translations", "de.csv")
# 		if os.path.exists(tpath):
# 			os.remove(tpath)
# 		finergy.translate.write_translations_file("finergy", "de")
# 		self.assertTrue(os.path.exists(tpath))
# 		self.assertEqual(dict(finergy.translate.read_csv_file(tpath)).get("Row"), "Reihe")
#
# 	def test_get_dict(self):
# 		finergy.local.lang = "de"
# 		self.assertEqual(finergy.get_lang_dict("doctype", "Role").get("Role"), "Rolle")
# 		finergy.local.lang = "en"
#
# if __name__=="__main__":
# 	finergy.connect("site1")
# 	unittest.main()
