# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

"""assign/unassign to ToDo"""

import json

import finergy
import finergy.share
import finergy.utils
from finergy import _
from finergy.desk.doctype.notification_log.notification_log import (
	enqueue_create_notification,
	get_title,
	get_title_html,
)
from finergy.desk.form.document_follow import follow_document


class DuplicateToDoError(finergy.ValidationError):
	pass


def get(args=None):
	"""get assigned to"""
	if not args:
		args = finergy.local.form_dict

	return finergy.get_all(
		"ToDo",
		fields=["owner", "name"],
		filters=dict(
			reference_type=args.get("doctype"), reference_name=args.get("name"), status=("!=", "Cancelled")
		),
		limit=5,
	)


@finergy.whitelist()
def add(args=None):
	"""add in someone's to do list
	args = {
	        "assign_to": [],
	        "doctype": ,
	        "name": ,
	        "description": ,
	        "assignment_rule":
	}

	"""
	if not args:
		args = finergy.local.form_dict

	users_with_duplicate_todo = []
	shared_with_users = []

	for assign_to in finergy.parse_json(args.get("assign_to")):
		filters = {
			"reference_type": args["doctype"],
			"reference_name": args["name"],
			"status": "Open",
			"owner": assign_to,
		}

		if finergy.get_all("ToDo", filters=filters):
			users_with_duplicate_todo.append(assign_to)
		else:
			from finergy.utils import nowdate

			if not args.get("description"):
				args["description"] = _("Assignment for {0} {1}").format(args["doctype"], args["name"])

			d = finergy.get_doc(
				{
					"doctype": "ToDo",
					"owner": assign_to,
					"reference_type": args["doctype"],
					"reference_name": args["name"],
					"description": args.get("description"),
					"priority": args.get("priority", "Medium"),
					"status": "Open",
					"date": args.get("date", nowdate()),
					"assigned_by": args.get("assigned_by", finergy.session.user),
					"assignment_rule": args.get("assignment_rule"),
				}
			).insert(ignore_permissions=True)

			# set assigned_to if field exists
			if finergy.get_meta(args["doctype"]).get_field("assigned_to"):
				finergy.db.set_value(args["doctype"], args["name"], "assigned_to", assign_to)

			doc = finergy.get_doc(args["doctype"], args["name"])

			# if assignee does not have permissions, share
			if not finergy.has_permission(doc=doc, user=assign_to):
				finergy.share.add(doc.doctype, doc.name, assign_to)
				shared_with_users.append(assign_to)

			# make this document followed by assigned user
			follow_document(args["doctype"], args["name"], assign_to)

			# notify
			notify_assignment(
				d.assigned_by,
				d.owner,
				d.reference_type,
				d.reference_name,
				action="ASSIGN",
				description=args.get("description"),
			)

	if shared_with_users:
		user_list = format_message_for_assign_to(shared_with_users)
		finergy.msgprint(
			_("Shared with the following Users with Read access:{0}").format(user_list, alert=True)
		)

	if users_with_duplicate_todo:
		user_list = format_message_for_assign_to(users_with_duplicate_todo)
		finergy.msgprint(_("Already in the following Users ToDo list:{0}").format(user_list, alert=True))

	return get(args)


@finergy.whitelist()
def add_multiple(args=None):
	if not args:
		args = finergy.local.form_dict

	docname_list = json.loads(args["name"])

	for docname in docname_list:
		args.update({"name": docname})
		add(args)


def close_all_assignments(doctype, name):
	assignments = finergy.db.get_all(
		"ToDo",
		fields=["owner"],
		filters=dict(reference_type=doctype, reference_name=name, status=("!=", "Cancelled")),
	)
	if not assignments:
		return False

	for assign_to in assignments:
		set_status(doctype, name, assign_to.owner, status="Closed")

	return True


@finergy.whitelist()
def remove(doctype, name, assign_to):
	return set_status(doctype, name, assign_to, status="Cancelled")


def set_status(doctype, name, assign_to, status="Cancelled"):
	"""remove from todo"""
	try:
		todo = finergy.db.get_value(
			"ToDo",
			{
				"reference_type": doctype,
				"reference_name": name,
				"owner": assign_to,
				"status": ("!=", status),
			},
		)
		if todo:
			todo = finergy.get_doc("ToDo", todo)
			todo.status = status
			todo.save(ignore_permissions=True)

			notify_assignment(todo.assigned_by, todo.owner, todo.reference_type, todo.reference_name)
	except finergy.DoesNotExistError:
		pass

	# clear assigned_to if field exists
	if finergy.get_meta(doctype).get_field("assigned_to") and status == "Cancelled":
		finergy.db.set_value(doctype, name, "assigned_to", None)

	return get({"doctype": doctype, "name": name})


def clear(doctype, name):
	"""
	Clears assignments, return False if not assigned.
	"""
	assignments = finergy.db.get_all(
		"ToDo", fields=["owner"], filters=dict(reference_type=doctype, reference_name=name)
	)
	if not assignments:
		return False

	for assign_to in assignments:
		set_status(doctype, name, assign_to.owner, "Cancelled")

	return True


def notify_assignment(assigned_by, owner, doc_type, doc_name, action="CLOSE", description=None):
	"""
	Notify assignee that there is a change in assignment
	"""
	if not (assigned_by and owner and doc_type and doc_name):
		return

	# return if self assigned or user disabled
	if assigned_by == owner or not finergy.db.get_value("User", owner, "enabled"):
		return

	# Search for email address in description -- i.e. assignee
	user_name = finergy.get_cached_value("User", finergy.session.user, "full_name")
	title = get_title(doc_type, doc_name)
	description_html = "<div>{0}</div>".format(description) if description else None

	if action == "CLOSE":
		subject = _("Your assignment on {0} {1} has been removed by {2}").format(
			finergy.bold(doc_type), get_title_html(title), finergy.bold(user_name)
		)
	else:
		user_name = finergy.bold(user_name)
		document_type = finergy.bold(doc_type)
		title = get_title_html(title)
		subject = _("{0} assigned a new task {1} {2} to you").format(user_name, document_type, title)

	notification_doc = {
		"type": "Assignment",
		"document_type": doc_type,
		"subject": subject,
		"document_name": doc_name,
		"from_user": finergy.session.user,
		"email_content": description_html,
	}

	enqueue_create_notification(owner, notification_doc)


def format_message_for_assign_to(users):
	return "<br><br>" + "<br>".join(users)
