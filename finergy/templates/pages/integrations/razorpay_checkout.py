# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import json

from six import string_types

import finergy
from finergy import _
from finergy.utils import cint, flt

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
)


def get_context(context):
	context.no_cache = 1
	context.api_key = get_api_key()

	try:
		doc = finergy.get_doc("Integration Request", finergy.form_dict["token"])
		payment_details = json.loads(doc.data)

		for key in expected_keys:
			context[key] = payment_details[key]

		context["token"] = finergy.form_dict["token"]
		context["amount"] = flt(context["amount"])
		context["subscription_id"] = (
			payment_details["subscription_id"] if payment_details.get("subscription_id") else ""
		)

	except Exception as e:
		finergy.redirect_to_message(
			_("Invalid Token"),
			_("Seems token you are using is invalid!"),
			http_status_code=400,
			indicator_color="red",
		)

		finergy.local.flags.redirect_location = finergy.local.response.location
		raise finergy.Redirect


def get_api_key():
	api_key = finergy.db.get_value("Razorpay Settings", None, "api_key")
	if cint(finergy.form_dict.get("use_sandbox")):
		api_key = finergy.conf.sandbox_api_key

	return api_key


@finergy.whitelist(allow_guest=True)
def make_payment(razorpay_payment_id, options, reference_doctype, reference_docname, token):
	data = {}

	if isinstance(options, string_types):
		data = json.loads(options)

	data.update(
		{
			"razorpay_payment_id": razorpay_payment_id,
			"reference_docname": reference_docname,
			"reference_doctype": reference_doctype,
			"token": token,
		}
	)

	data = finergy.get_doc("Razorpay Settings").create_request(data)
	finergy.db.commit()
	return data
