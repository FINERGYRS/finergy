# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import datetime
import json

from six import string_types, text_type
from six.moves.urllib.parse import parse_qs

import finergy
from finergy import _
from finergy.utils import get_request_session


def make_request(method, url, auth=None, headers=None, data=None):
	auth = auth or ""
	data = data or {}
	headers = headers or {}

	try:
		s = get_request_session()
		finergy.flags.integration_request = s.request(method, url, data=data, auth=auth, headers=headers)
		finergy.flags.integration_request.raise_for_status()

		if finergy.flags.integration_request.headers.get("content-type") == "text/plain; charset=utf-8":
			return parse_qs(finergy.flags.integration_request.text)

		return finergy.flags.integration_request.json()
	except Exception as exc:
		finergy.log_error()
		raise exc


def make_get_request(url, **kwargs):
	return make_request("GET", url, **kwargs)


def make_post_request(url, **kwargs):
	return make_request("POST", url, **kwargs)


def make_put_request(url, **kwargs):
	return make_request("PUT", url, **kwargs)


def create_request_log(data, integration_type, service_name, name=None, error=None):
	if isinstance(data, string_types):
		data = json.loads(data)

	if isinstance(error, string_types):
		error = json.loads(error)

	integration_request = finergy.get_doc(
		{
			"doctype": "Integration Request",
			"integration_type": integration_type,
			"integration_request_service": service_name,
			"reference_doctype": data.get("reference_doctype"),
			"reference_docname": data.get("reference_docname"),
			"error": json.dumps(error, default=json_handler),
			"data": json.dumps(data, default=json_handler),
		}
	)

	if name:
		integration_request.flags._name = name

	integration_request.insert(ignore_permissions=True)
	finergy.db.commit()

	return integration_request


def get_payment_gateway_controller(payment_gateway):
	"""Return payment gateway controller"""
	gateway = finergy.get_doc("Payment Gateway", payment_gateway)
	if gateway.gateway_controller is None:
		try:
			return finergy.get_doc("{0} Settings".format(payment_gateway))
		except Exception:
			finergy.throw(_("{0} Settings not found").format(payment_gateway))
	else:
		try:
			return finergy.get_doc(gateway.gateway_settings, gateway.gateway_controller)
		except Exception:
			finergy.throw(_("{0} Settings not found").format(payment_gateway))


@finergy.whitelist(allow_guest=True, xss_safe=True)
def get_checkout_url(**kwargs):
	try:
		if kwargs.get("payment_gateway"):
			doc = finergy.get_doc("{0} Settings".format(kwargs.get("payment_gateway")))
			return doc.get_payment_url(**kwargs)
		else:
			raise Exception
	except Exception:
		finergy.respond_as_web_page(
			_("Something went wrong"),
			_(
				"Looks like something is wrong with this site's payment gateway configuration. No payment has been made."
			),
			indicator_color="red",
			http_status_code=finergy.ValidationError.http_status_code,
		)


def create_payment_gateway(gateway, settings=None, controller=None):
	# NOTE: we don't translate Payment Gateway name because it is an internal doctype
	if not finergy.db.exists("Payment Gateway", gateway):
		payment_gateway = finergy.get_doc(
			{
				"doctype": "Payment Gateway",
				"gateway": gateway,
				"gateway_settings": settings,
				"gateway_controller": controller,
			}
		)
		payment_gateway.insert(ignore_permissions=True)


def json_handler(obj):
	if isinstance(obj, (datetime.date, datetime.timedelta, datetime.datetime)):
		return text_type(obj)
