# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import print_function, unicode_literals

no_cache = 1
base_template_path = "templates/www/app.html"

import os
import re

import finergy
import finergy.sessions
from finergy import _
from finergy.utils.jinja import is_rtl


def get_context(context):
	if finergy.session.user == "Guest":
		finergy.throw(_("Log in to access this page."), finergy.PermissionError)
	elif finergy.db.get_value("User", finergy.session.user, "user_type") == "Website User":
		finergy.throw(_("You are not permitted to access this page."), finergy.PermissionError)

	hooks = finergy.get_hooks()
	try:
		boot = finergy.sessions.get()
	except Exception as e:
		boot = finergy._dict(status="failed", error=str(e))
		print(finergy.get_traceback())

	# this needs commit
	csrf_token = finergy.sessions.get_csrf_token()

	finergy.db.commit()

	desk_theme = finergy.db.get_value("User", finergy.session.user, "desk_theme")

	boot_json = finergy.as_json(boot)

	# remove script tags from boot
	boot_json = re.sub(r"\<script[^<]*\</script\>", "", boot_json)

	# TODO: Find better fix
	boot_json = re.sub(r"</script\>", "", boot_json)

	style_urls = hooks["app_include_css"]

	context.update(
		{
			"no_cache": 1,
			"build_version": finergy.utils.get_build_version(),
			"include_js": hooks["app_include_js"],
			"include_css": get_rtl_styles(style_urls) if is_rtl() else style_urls,
			"layout_direction": "rtl" if is_rtl() else "ltr",
			"lang": finergy.local.lang,
			"sounds": hooks["sounds"],
			"boot": boot if context.get("for_mobile") else boot_json,
			"desk_theme": desk_theme or "Light",
			"csrf_token": csrf_token,
			"google_analytics_id": finergy.conf.get("google_analytics_id"),
			"google_analytics_anonymize_ip": finergy.conf.get("google_analytics_anonymize_ip"),
			"mixpanel_id": finergy.conf.get("mixpanel_id"),
		}
	)

	return context


def get_rtl_styles(style_urls):
	rtl_style_urls = []
	for style_url in style_urls:
		rtl_style_urls.append(style_url.replace("/css/", "/css-rtl/"))
	return rtl_style_urls


@finergy.whitelist()
def get_desk_assets(build_version):
	"""Get desk assets to be loaded for mobile app"""
	data = get_context({"for_mobile": True})
	assets = [{"type": "js", "data": ""}, {"type": "css", "data": ""}]

	if build_version != data["build_version"]:
		# new build, send assets
		for path in data["include_js"]:
			# assets path shouldn't start with /
			# as it points to different location altogether
			if path.startswith("/assets/"):
				path = path.replace("/assets/", "assets/")
			try:
				with open(os.path.join(finergy.local.sites_path, path), "r") as f:
					assets[0]["data"] = assets[0]["data"] + "\n" + finergy.safe_decode(f.read(), "utf-8")
			except IOError:
				pass

		for path in data["include_css"]:
			if path.startswith("/assets/"):
				path = path.replace("/assets/", "assets/")
			try:
				with open(os.path.join(finergy.local.sites_path, path), "r") as f:
					assets[1]["data"] = assets[1]["data"] + "\n" + finergy.safe_decode(f.read(), "utf-8")
			except IOError:
				pass

	return {"build_version": data["build_version"], "boot": data["boot"], "assets": assets}
