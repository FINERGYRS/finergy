# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# See license.txt

from __future__ import unicode_literals

import finergy

no_cache = True


def get_context(context):
	token = finergy.local.form_dict.token
	doc = finergy.get_doc(finergy.local.form_dict.doctype, finergy.local.form_dict.docname)

	context.payment_message = ""
	if hasattr(doc, "get_payment_success_message"):
		context.payment_message = doc.get_payment_success_message()
