# Copyright (c) 2018, Finergy Reporting Solutions SAS and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import json

import finergy
from finergy import _
from finergy.integrations.doctype.braintree_settings.braintree_settings import (
	get_client_token,
	get_gateway_controller,
)
from finergy.utils import flt

no_cache = 1

expected_keys = (
	"amount",
	"title",
	"description",
	"reference_doctype",
	"reference_docname",
	"payer_name",
	"payer_email",
	"order_id",
	"currency",
)


def get_context(context):
	context.no_cache = 1

	# all these keys exist in form_dict
	if not (set(expected_keys) - set(list(finergy.form_dict))):
		for key in expected_keys:
			context[key] = finergy.form_dict[key]

		context.client_token = get_client_token(context.reference_docname)

		context["amount"] = flt(context["amount"])

		gateway_controller = get_gateway_controller(context.reference_docname)
		context["header_img"] = finergy.db.get_value(
			"Braintree Settings", gateway_controller, "header_img"
		)

	else:
		finergy.redirect_to_message(
			_("Some information is missing"),
			_("Looks like someone sent you to an incomplete URL. Please ask them to look into it."),
		)
		finergy.local.flags.redirect_location = finergy.local.response.location
		raise finergy.Redirect


@finergy.whitelist(allow_guest=True)
def make_payment(payload_nonce, data, reference_doctype, reference_docname):
	data = json.loads(data)

	data.update({"payload_nonce": payload_nonce})

	gateway_controller = get_gateway_controller(reference_docname)
	data = finergy.get_doc("Braintree Settings", gateway_controller).create_payment_request(data)
	finergy.db.commit()
	return data
