# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import finergy
from finergy.model.document import Document


class DiscussionTopic(Document):
	pass


@finergy.whitelist()
def submit_discussion(doctype, docname, reply, title, topic_name=None):
	if topic_name:
		save_message(reply, topic_name)
		return topic_name

	topic = finergy.get_doc(
		{
			"doctype": "Discussion Topic",
			"title": title,
			"reference_doctype": doctype,
			"reference_docname": docname,
		}
	)
	topic.save(ignore_permissions=True)
	save_message(reply, topic.name)
	return topic.name


def save_message(reply, topic):
	finergy.get_doc({"doctype": "Discussion Reply", "reply": reply, "topic": topic}).save(
		ignore_permissions=True
	)


@finergy.whitelist(allow_guest=True)
def get_docname(route):
	if not route:
		route = finergy.db.get_single_value("Website Settings", "home_page")
	return finergy.db.get_value("Web Page", {"route": route}, ["name"])
