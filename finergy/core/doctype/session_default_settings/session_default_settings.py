# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import finergy
from finergy import _
from finergy.model.document import Document


class SessionDefaultSettings(Document):
	pass


@finergy.whitelist()
def get_session_default_values():
	settings = finergy.get_single("Session Default Settings")
	fields = []
	for default_values in settings.session_defaults:
		reference_doctype = finergy.scrub(default_values.ref_doctype)
		fields.append(
			{
				"fieldname": reference_doctype,
				"fieldtype": "Link",
				"options": default_values.ref_doctype,
				"label": _("Default {0}").format(_(default_values.ref_doctype)),
				"default": finergy.defaults.get_user_default(reference_doctype),
			}
		)
	return json.dumps(fields)


@finergy.whitelist()
def set_session_default_values(default_values):
	default_values = finergy.parse_json(default_values)
	for entry in default_values:
		try:
			finergy.defaults.set_user_default(entry, default_values.get(entry))
		except Exception:
			return
	return "success"


# called on hook 'on_logout' to clear defaults for the session
def clear_session_defaults():
	settings = finergy.get_single("Session Default Settings").session_defaults
	for entry in settings:
		finergy.defaults.clear_user_default(finergy.scrub(entry.ref_doctype))
