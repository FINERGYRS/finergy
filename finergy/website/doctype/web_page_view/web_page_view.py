# -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class WebPageView(Document):
	pass


@finergy.whitelist(allow_guest=True)
def make_view_log(path, referrer=None, browser=None, version=None, url=None, user_tz=None):
	if not is_tracking_enabled():
		return

	request_dict = finergy.request.__dict__
	user_agent = request_dict.get("environ", {}).get("HTTP_USER_AGENT")

	if referrer:
		referrer = referrer.split("?")[0]

	is_unique = True
	if referrer.startswith(url):
		is_unique = False

	if path != "/" and path.startswith("/"):
		path = path[1:]

	view = finergy.new_doc("Web Page View")
	view.path = path
	view.referrer = referrer
	view.browser = browser
	view.browser_version = version
	view.time_zone = user_tz
	view.user_agent = user_agent
	view.is_unique = is_unique

	try:
		view.insert(ignore_permissions=True)
	except Exception:
		if finergy.message_log:
			finergy.message_log.pop()


@finergy.whitelist()
def get_page_view_count(path):
	return finergy.db.count("Web Page View", filters={"path": path})


def is_tracking_enabled():
	return finergy.db.get_value("Website Settings", "Website Settings", "enable_view_tracking")
