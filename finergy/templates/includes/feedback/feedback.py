# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import finergy
from finergy import _
from finergy.rate_limiter import rate_limit
from finergy.website.doctype.blog_settings.blog_settings import get_feedback_limit


@finergy.whitelist(allow_guest=True)
@rate_limit(key="reference_name", limit=get_feedback_limit, seconds=60 * 60)
def add_feedback(reference_doctype, reference_name, rating, feedback):
	doc = finergy.get_doc(reference_doctype, reference_name)
	if doc.disable_feedback == 1:
		return

	doc = finergy.new_doc("Feedback")
	doc.reference_doctype = reference_doctype
	doc.reference_name = reference_name
	doc.rating = rating
	doc.feedback = feedback
	doc.ip_address = finergy.local.request_ip
	doc.save(ignore_permissions=True)

	subject = _("New Feedback on {0}: {1}").format(reference_doctype, reference_name)
	send_mail(doc, subject)
	return doc


@finergy.whitelist()
def update_feedback(reference_doctype, reference_name, rating, feedback):
	doc = finergy.get_doc(reference_doctype, reference_name)
	if doc.disable_feedback == 1:
		return

	filters = {
		"owner": finergy.session.user,
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
	}
	d = finergy.get_all("Feedback", filters=filters, limit=1)
	doc = finergy.get_doc("Feedback", d[0].name)
	doc.rating = rating
	doc.feedback = feedback
	doc.save(ignore_permissions=True)

	subject = _("Feedback updated on {0}: {1}").format(reference_doctype, reference_name)
	send_mail(doc, subject)
	return doc


def send_mail(feedback, subject):
	doc = finergy.get_doc(feedback.reference_doctype, feedback.reference_name)

	message = "<p>{0} ({1})</p>".format(
		feedback.feedback, feedback.rating
	) + "<p><a href='{0}/app/feedback/{1}' style='font-size: 80%'>{2}</a></p>".format(
		finergy.utils.get_request_site_address(), feedback.name, _("View Feedback")
	)

	# notify creator
	finergy.sendmail(
		recipients=finergy.db.get_value("User", doc.owner, "email") or doc.owner,
		subject=subject,
		message=message,
		reference_doctype=doc.doctype,
		reference_name=doc.name,
	)
