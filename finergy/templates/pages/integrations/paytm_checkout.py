# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import json

import finergy
from finergy import _
from finergy.integrations.doctype.paytm_settings.paytm_settings import (
	get_paytm_config,
	get_paytm_params,
)


def get_context(context):
	context.no_cache = 1
	paytm_config = get_paytm_config()

	try:
		doc = finergy.get_doc("Integration Request", finergy.form_dict["order_id"])

		context.payment_details = get_paytm_params(json.loads(doc.data), doc.name, paytm_config)

		context.url = paytm_config.url

	except Exception:
		finergy.log_error()
		finergy.redirect_to_message(
			_("Invalid Token"),
			_("Seems token you are using is invalid!"),
			http_status_code=400,
			indicator_color="red",
		)

		finergy.local.flags.redirect_location = finergy.local.response.location
		raise finergy.Redirect
