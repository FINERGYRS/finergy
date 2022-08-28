# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import finergy
from finergy import _


@finergy.whitelist()
def update_event(args, field_map):
	"""Updates Event (called via calendar) based on passed `field_map`"""
	args = finergy._dict(json.loads(args))
	field_map = finergy._dict(json.loads(field_map))
	w = finergy.get_doc(args.doctype, args.name)
	w.set(field_map.start, args[field_map.start])
	w.set(field_map.end, args.get(field_map.end))
	w.save()


def get_event_conditions(doctype, filters=None):
	"""Returns SQL conditions with user permissions and filters for event queries"""
	from finergy.desk.reportview import get_filters_cond

	if not finergy.has_permission(doctype):
		finergy.throw(_("Not Permitted"), finergy.PermissionError)

	return get_filters_cond(doctype, filters, [], with_match_conditions=True)


@finergy.whitelist()
def get_events(doctype, start, end, field_map, filters=None, fields=None):

	field_map = finergy._dict(json.loads(field_map))
	fields = finergy.parse_json(fields)

	doc_meta = finergy.get_meta(doctype)
	for d in doc_meta.fields:
		if d.fieldtype == "Color":
			field_map.update({"color": d.fieldname})

	if filters:
		filters = json.loads(filters or "")

	if not fields:
		fields = [field_map.start, field_map.end, field_map.title, "name"]

	if field_map.color:
		fields.append(field_map.color)

	start_date = "ifnull(%s, '0001-01-01 00:00:00')" % field_map.start
	end_date = "ifnull(%s, '2199-12-31 00:00:00')" % field_map.end

	filters += [
		[doctype, start_date, "<=", end],
		[doctype, end_date, ">=", start],
	]

	return finergy.get_list(doctype, fields=fields, filters=filters)
