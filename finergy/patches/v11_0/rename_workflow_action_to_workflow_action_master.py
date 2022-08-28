from __future__ import unicode_literals

import finergy
from finergy.model.rename_doc import rename_doc


def execute():
	if finergy.db.table_exists("Workflow Action") and not finergy.db.table_exists(
		"Workflow Action Master"
	):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		finergy.reload_doc("workflow", "doctype", "workflow_action_master")
