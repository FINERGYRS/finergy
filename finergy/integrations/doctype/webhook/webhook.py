# -*- coding: utf-8 -*-
# Copyright (c) 2017, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import base64
import datetime
import hashlib
import hmac
import json
from time import sleep

import requests
from six.moves.urllib.parse import urlparse

import finergy
from finergy import _
from finergy.model.document import Document
from finergy.utils.jinja import validate_template
from finergy.utils.safe_exec import get_safe_globals

WEBHOOK_SECRET_HEADER = "X-Finergy-Webhook-Signature"


class Webhook(Document):
	def validate(self):
		self.validate_docevent()
		self.validate_condition()
		self.validate_request_url()
		self.validate_request_body()
		self.validate_repeating_fields()

	def on_update(self):
		finergy.cache().delete_value("webhooks")

	def validate_docevent(self):
		if self.webhook_doctype:
			is_submittable = finergy.get_value("DocType", self.webhook_doctype, "is_submittable")
			if not is_submittable and self.webhook_docevent in [
				"on_submit",
				"on_cancel",
				"on_update_after_submit",
			]:
				finergy.throw(_("DocType must be Submittable for the selected Doc Event"))

	def validate_condition(self):
		temp_doc = finergy.new_doc(self.webhook_doctype)
		if self.condition:
			try:
				finergy.safe_eval(self.condition, eval_locals=get_context(temp_doc))
			except Exception as e:
				finergy.throw(_("Invalid Condition: {}").format(e))

	def validate_request_url(self):
		try:
			request_url = urlparse(self.request_url).netloc
			if not request_url:
				raise finergy.ValidationError
		except Exception as e:
			finergy.throw(_("Check Request URL"), exc=e)

	def validate_request_body(self):
		if self.request_structure:
			if self.request_structure == "Form URL-Encoded":
				self.webhook_json = None
			elif self.request_structure == "JSON":
				validate_template(self.webhook_json)
				self.webhook_data = []

	def validate_repeating_fields(self):
		"""Error when Same Field is entered multiple times in webhook_data"""
		webhook_data = []
		for entry in self.webhook_data:
			webhook_data.append(entry.fieldname)

		if len(webhook_data) != len(set(webhook_data)):
			finergy.throw(_("Same Field is entered more than once"))


def get_context(doc):
	return {"doc": doc, "utils": get_safe_globals().get("finergy").get("utils")}


def enqueue_webhook(doc, webhook):
	webhook = finergy.get_doc("Webhook", webhook.get("name"))
	headers = get_webhook_headers(doc, webhook)
	data = get_webhook_data(doc, webhook)

	for i in range(3):
		try:
			r = requests.request(
				method=webhook.request_method,
				url=webhook.request_url,
				data=json.dumps(data, default=str),
				headers=headers,
				timeout=5,
			)
			r.raise_for_status()
			finergy.logger().debug({"webhook_success": r.text})
			log_request(webhook.request_url, headers, data, r)
			break
		except Exception as e:
			finergy.logger().debug({"webhook_error": e, "try": i + 1})
			log_request(webhook.request_url, headers, data, r)
			sleep(3 * i + 1)
			if i != 2:
				continue
			else:
				raise e


def log_request(url, headers, data, res):
	request_log = finergy.get_doc(
		{
			"doctype": "Webhook Request Log",
			"user": finergy.session.user if finergy.session.user else None,
			"url": url,
			"headers": finergy.as_json(headers) if headers else None,
			"data": finergy.as_json(data) if data else None,
			"response": finergy.as_json(res.json()) if res else None,
		}
	)

	request_log.save(ignore_permissions=True)


def get_webhook_headers(doc, webhook):
	headers = {}

	if webhook.enable_security:
		data = get_webhook_data(doc, webhook)
		signature = base64.b64encode(
			hmac.new(
				webhook.get_password("webhook_secret").encode("utf8"),
				json.dumps(data).encode("utf8"),
				hashlib.sha256,
			).digest()
		)
		headers[WEBHOOK_SECRET_HEADER] = signature

	if webhook.webhook_headers:
		for h in webhook.webhook_headers:
			if h.get("key") and h.get("value"):
				headers[h.get("key")] = h.get("value")

	return headers


def get_webhook_data(doc, webhook):
	data = {}
	doc = doc.as_dict(convert_dates_to_str=True)

	if webhook.webhook_data:
		data = {w.key: doc.get(w.fieldname) for w in webhook.webhook_data}
	elif webhook.webhook_json:
		data = finergy.render_template(webhook.webhook_json, get_context(doc))
		data = json.loads(data)

	return data
