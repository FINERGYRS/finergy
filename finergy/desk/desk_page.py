# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy
from finergy.translate import send_translations


@finergy.whitelist()
def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = finergy.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = finergy._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		finergy.response["403"] = 1
		raise finergy.PermissionError("No read permission for Page %s" % (page.title or name))


@finergy.whitelist(allow_guest=True)
def getpage():
	"""
	Load the page from `finergy.form` and send it via `finergy.response`
	"""
	page = finergy.form_dict.get("name")
	doc = get(page)

	# load translations
	if finergy.lang != "en":
		send_translations(finergy.get_lang_dict("page", page))

	finergy.response.docs.append(doc)


def has_permission(page):
	if finergy.session.user == "Administrator" or "System Manager" in finergy.get_roles():
		return True

	page_roles = [d.role for d in page.get("roles")]
	if page_roles:
		if finergy.session.user == "Guest" and "Guest" not in page_roles:
			return False
		elif not set(page_roles).intersection(set(finergy.get_roles())):
			# check if roles match
			return False

	if not finergy.has_permission("Page", ptype="read", doc=page):
		# check if there are any user_permissions
		return False
	else:
		# hack for home pages! if no Has Roles, allow everyone to see!
		return True
