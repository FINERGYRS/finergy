# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

import finergy
from finergy.search.full_text_search import FullTextSearch
from finergy.search.website_search import WebsiteSearch
from finergy.utils import cint


@finergy.whitelist(allow_guest=True)
def web_search(query, scope=None, limit=20):
	limit = cint(limit)
	ws = WebsiteSearch(index_name="web_routes")
	return ws.search(query, scope, limit)
