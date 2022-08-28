# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from six.moves.urllib.parse import parse_qsl

import finergy
from finergy import _
from finergy.twofactor import get_qr_svg_code


def get_context(context):
	context.no_cache = 1
	context.qr_code_user, context.qrcode_svg = get_user_svg_from_cache()


def get_query_key():
	"""Return query string arg."""
	query_string = finergy.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if not "k" in list(query):
		finergy.throw(_("Not Permitted"), finergy.PermissionError)
	query = (query["k"]).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		finergy.throw(_("Not Permitted"), finergy.PermissionError)
	return query


def get_user_svg_from_cache():
	"""Get User and SVG code from cache."""
	key = get_query_key()
	totp_uri = finergy.cache().get_value("{}_uri".format(key))
	user = finergy.cache().get_value("{}_user".format(key))
	if not totp_uri or not user:
		finergy.throw(_("Page has expired!"), finergy.PermissionError)
	if not finergy.db.exists("User", user):
		finergy.throw(_("Not Permitted"), finergy.PermissionError)
	user = finergy.get_doc("User", user)
	svg = get_qr_svg_code(totp_uri)
	return (user, svg.decode())
