# -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import finergy
from finergy.model.document import Document


class ListViewSettings(Document):
	def on_update(self):
		finergy.clear_document_cache(self.doctype, self.name)


@finergy.whitelist()
def save_listview_settings(doctype, listview_settings, removed_listview_fields):

	listview_settings = finergy.parse_json(listview_settings)
	removed_listview_fields = finergy.parse_json(removed_listview_fields)

	if finergy.get_all("List View Settings", filters={"name": doctype}):
		doc = finergy.get_doc("List View Settings", doctype)
		doc.update(listview_settings)
		doc.save()
	else:
		doc = finergy.new_doc("List View Settings")
		doc.name = doctype
		doc.update(listview_settings)
		doc.insert()

	set_listview_fields(doctype, listview_settings.get("fields"), removed_listview_fields)

	return {"meta": finergy.get_meta(doctype, False), "listview_settings": doc}


def set_listview_fields(doctype, listview_fields, removed_listview_fields):
	meta = finergy.get_meta(doctype)

	listview_fields = [
		f.get("fieldname") for f in finergy.parse_json(listview_fields) if f.get("fieldname")
	]

	for field in removed_listview_fields:
		set_in_list_view_property(doctype, meta.get_field(field), "0")

	for field in listview_fields:
		set_in_list_view_property(doctype, meta.get_field(field), "1")


def set_in_list_view_property(doctype, field, value):
	if not field or field.fieldname == "status_field":
		return

	property_setter = finergy.db.get_value(
		"Property Setter",
		{"doc_type": doctype, "field_name": field.fieldname, "property": "in_list_view"},
	)
	if property_setter:
		doc = finergy.get_doc("Property Setter", property_setter)
		doc.value = value
		doc.save()
	else:
		finergy.make_property_setter(
			{
				"doctype": doctype,
				"doctype_or_field": "DocField",
				"fieldname": field.fieldname,
				"property": "in_list_view",
				"value": value,
				"property_type": "Check",
			},
			ignore_validate=True,
		)


@finergy.whitelist()
def get_default_listview_fields(doctype):
	meta = finergy.get_meta(doctype)
	path = finergy.get_module_path(
		finergy.scrub(meta.module), "doctype", finergy.scrub(meta.name), finergy.scrub(meta.name) + ".json"
	)
	doctype_json = finergy.get_file_json(path)

	fields = [f.get("fieldname") for f in doctype_json.get("fields") if f.get("in_list_view")]

	if meta.title_field:
		if not meta.title_field.strip() in fields:
			fields.append(meta.title_field.strip())

	return fields
