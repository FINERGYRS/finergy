from __future__ import unicode_literals

import finergy


def execute():
	finergy.reload_doc("workflow", "doctype", "workflow_transition")
	finergy.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
