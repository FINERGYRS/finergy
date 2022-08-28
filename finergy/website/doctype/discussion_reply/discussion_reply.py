# Copyright (c) 2021, FOSS United and contributors
# For license information, please see license.txt

import finergy
from finergy.model.document import Document


class DiscussionReply(Document):
	def after_insert(self):

		replies = finergy.db.count("Discussion Reply", {"topic": self.topic})
		template = finergy.render_template(
			"finergy/templates/discussions/reply_card.html",
			{"reply": self, "topic": {"name": self.topic}, "loop": {"index": replies}},
		)

		topic_info = finergy.get_all(
			"Discussion Topic",
			{"name": self.topic},
			["reference_doctype", "reference_docname", "name", "title", "owner", "creation"],
		)

		sidebar = finergy.render_template(
			"finergy/templates/discussions/sidebar.html", {"topic": topic_info[0]}
		)

		new_topic_template = finergy.render_template(
			"finergy/templates/discussions/reply_section.html", {"topics": topic_info}
		)

		finergy.publish_realtime(
			event="publish_message",
			message={
				"template": template,
				"topic_info": topic_info[0],
				"sidebar": sidebar,
				"new_topic_template": new_topic_template,
			},
			after_commit=True,
		)
