# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy
from finergy.utils import strip_html_tags

no_cache = 1


def get_context(context):
	message_context = {}
	if hasattr(finergy.local, "message"):
		message_context["header"] = finergy.local.message_title
		message_context["title"] = strip_html_tags(finergy.local.message_title)
		message_context["message"] = finergy.local.message
		if hasattr(finergy.local, "message_success"):
			message_context["success"] = finergy.local.message_success

	elif finergy.local.form_dict.id:
		message_id = finergy.local.form_dict.id
		key = "message_id:{0}".format(message_id)
		message = finergy.cache().get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				finergy.local.response["http_status_code"] = message["http_status_code"]

	return message_context
