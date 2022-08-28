# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from six import iteritems
from six.moves.urllib.parse import quote, urljoin

import finergy
from finergy.model.document import get_controller
from finergy.utils import get_datetime, get_url, nowdate
from finergy.website.router import get_all_page_context_from_doctypes, get_pages

no_cache = 1
base_template_path = "templates/www/sitemap.xml"


def get_context(context):
	"""generate the sitemap XML"""

	# the site might be accessible from multiple host_names
	# for e.g gadgets.capkpi.com and gadgetsinternational.com
	# so it should be picked from the request
	host = finergy.utils.get_host_name_from_request()

	links = []
	for route, page in iteritems(get_pages()):
		if page.sitemap:
			links.append({"loc": get_url(quote(page.name.encode("utf-8"))), "lastmod": nowdate()})

	for route, data in iteritems(get_public_pages_from_doctypes()):
		links.append(
			{
				"loc": get_url(quote((route or "").encode("utf-8"))),
				"lastmod": get_datetime(data.get("modified")).strftime("%Y-%m-%d"),
			}
		)

	return {"links": links}


def get_public_pages_from_doctypes():
	"""Returns pages from doctypes that are publicly accessible"""

	def get_sitemap_routes():
		routes = {}
		doctypes_with_web_view = [
			d.name for d in finergy.db.get_all("DocType", {"has_web_view": 1, "allow_guest_to_view": 1})
		]

		for doctype in doctypes_with_web_view:
			controller = get_controller(doctype)
			meta = finergy.get_meta(doctype)
			condition_field = meta.is_published_field or controller.website.condition_field

			try:
				res = finergy.db.get_all(doctype, ["route", "name", "modified"], {condition_field: 1})
				for r in res:
					routes[r.route] = {"doctype": doctype, "name": r.name, "modified": r.modified}

			except Exception as e:
				if not finergy.db.is_missing_column(e):
					raise e

		return routes

	return finergy.cache().get_value("sitemap_routes", get_sitemap_routes)
