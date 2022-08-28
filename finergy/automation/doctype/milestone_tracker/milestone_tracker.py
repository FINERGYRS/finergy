# -*- coding: utf-8 -*-
# Copyright (c) 2019, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
import finergy.cache_manager
from finergy.model import log_types
from finergy.model.document import Document


class MilestoneTracker(Document):
	def on_update(self):
		finergy.cache_manager.clear_doctype_map("Milestone Tracker", self.document_type)

	def on_trash(self):
		finergy.cache_manager.clear_doctype_map("Milestone Tracker", self.document_type)

	def apply(self, doc):
		before_save = doc.get_doc_before_save()
		from_value = before_save and before_save.get(self.track_field) or None
		if from_value != doc.get(self.track_field):
			finergy.get_doc(
				dict(
					doctype="Milestone",
					reference_type=doc.doctype,
					reference_name=doc.name,
					track_field=self.track_field,
					from_value=from_value,
					value=doc.get(self.track_field),
					milestone_tracker=self.name,
				)
			).insert(ignore_permissions=True)


def evaluate_milestone(doc, event):
	if (
		finergy.flags.in_install
		or finergy.flags.in_migrate
		or finergy.flags.in_setup_wizard
		or doc.doctype in log_types
	):
		return

	# track milestones related to this doctype
	for d in get_milestone_trackers(doc.doctype):
		finergy.get_doc("Milestone Tracker", d.get("name")).apply(doc)


def get_milestone_trackers(doctype):
	return finergy.cache_manager.get_doctype_map(
		"Milestone Tracker", doctype, dict(document_type=doctype, disabled=0)
	)
