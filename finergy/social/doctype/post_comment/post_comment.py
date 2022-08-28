# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.core.doctype.user.user import extract_mentions
from finergy.model.document import Document


class PostComment(Document):
	def after_insert(self):
		mentions = extract_mentions(self.content)
		for mention in mentions:
			if mention == self.owner:
				continue
			finergy.publish_realtime(
				"mention",
				"""{} mentioned you!
				<br><a class="text-muted text-small" href="desk#social/home">Check Social<a>""".format(
					finergy.utils.get_fullname(self.owner)
				),
				user=mention,
				after_commit=True,
			)
		finergy.publish_realtime("new_post_comment" + self.parent, self, after_commit=True)
