from __future__ import unicode_literals

import unittest

import finergy
from finergy.utils import set_request
from finergy.website import render
from finergy.website.utils import get_home_page


class TestWebsite(unittest.TestCase):
	def test_home_page_for_role(self):
		finergy.delete_doc_if_exists("User", "test-user-for-home-page@example.com")
		finergy.delete_doc_if_exists("Role", "home-page-test")
		finergy.delete_doc_if_exists("Web Page", "home-page-test")
		user = finergy.get_doc(
			dict(doctype="User", email="test-user-for-home-page@example.com", first_name="test")
		).insert(ignore_if_duplicate=True)
		user.reload()

		role = finergy.get_doc(
			dict(doctype="Role", role_name="home-page-test", desk_access=0, home_page="/home-page-test")
		).insert()

		user.add_roles(role.name)
		user.save()

		finergy.set_user("test-user-for-home-page@example.com")
		self.assertEqual(get_home_page(), "home-page-test")

		finergy.set_user("Administrator")
		role.home_page = ""
		role.save()

		# home page via portal settings
		finergy.db.set_value("Portal Settings", None, "default_portal_home", "test-portal-home")

		finergy.set_user("test-user-for-home-page@example.com")
		finergy.cache().hdel("home_page", finergy.session.user)
		self.assertEqual(get_home_page(), "test-portal-home")

	def test_page_load(self):
		finergy.set_user("Guest")
		set_request(method="POST", path="login")
		response = render.render()

		self.assertEquals(response.status_code, 200)

		html = finergy.safe_decode(response.get_data())

		self.assertTrue("// login.js" in html)
		self.assertTrue("<!-- login.html -->" in html)
		finergy.set_user("Administrator")

	def test_redirect(self):
		import finergy.hooks

		finergy.hooks.website_redirects = [
			dict(source=r"/testfrom", target=r"://testto1"),
			dict(source=r"/testfromregex.*", target=r"://testto2"),
			dict(source=r"/testsub/(.*)", target=r"://testto3/\1"),
		]

		website_settings = finergy.get_doc("Website Settings")
		website_settings.append("route_redirects", {"source": "/testsource", "target": "/testtarget"})
		website_settings.save()

		finergy.cache().delete_key("app_hooks")
		finergy.cache().delete_key("website_redirects")

		set_request(method="GET", path="/testfrom")
		response = render.render()
		self.assertEquals(response.status_code, 301)
		self.assertEquals(response.headers.get("Location"), r"://testto1")

		set_request(method="GET", path="/testfromregex/test")
		response = render.render()
		self.assertEquals(response.status_code, 301)
		self.assertEquals(response.headers.get("Location"), r"://testto2")

		set_request(method="GET", path="/testsub/me")
		response = render.render()
		self.assertEquals(response.status_code, 301)
		self.assertEquals(response.headers.get("Location"), r"://testto3/me")

		set_request(method="GET", path="/test404")
		response = render.render()
		self.assertEquals(response.status_code, 404)

		set_request(method="GET", path="/testsource")
		response = render.render()
		self.assertEquals(response.status_code, 301)
		self.assertEquals(response.headers.get("Location"), "/testtarget")

		delattr(finergy.hooks, "website_redirects")
		finergy.cache().delete_key("app_hooks")
