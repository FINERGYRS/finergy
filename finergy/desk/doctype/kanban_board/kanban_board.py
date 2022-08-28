# -*- coding: utf-8 -*-
# Copyright (c) 2015, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

from six import iteritems

import finergy
from finergy import _
from finergy.model.document import Document


class KanbanBoard(Document):
	def validate(self):
		self.validate_column_name()

	def on_change(self):
		finergy.clear_cache(doctype=self.reference_doctype)
		finergy.cache().delete_keys("_user_settings")

	def before_insert(self):
		for column in self.columns:
			column.order = get_order_for_column(self, column.column_name)

	def validate_column_name(self):
		for column in self.columns:
			if not column.column_name:
				finergy.msgprint(_("Column Name cannot be empty"), raise_exception=True)


def get_permission_query_conditions(user):
	if not user:
		user = finergy.session.user

	if user == "Administrator":
		return ""

	return """(`tabKanban Board`.private=0 or `tabKanban Board`.owner={user})""".format(
		user=finergy.db.escape(user)
	)


def has_permission(doc, ptype, user):
	if doc.private == 0 or user == "Administrator":
		return True

	if user == doc.owner:
		return True

	return False


@finergy.whitelist()
def get_kanban_boards(doctype):
	"""Get Kanban Boards for doctype to show in List View"""
	return finergy.get_list(
		"Kanban Board",
		fields=["name", "filters", "reference_doctype", "private"],
		filters={"reference_doctype": doctype},
	)


@finergy.whitelist()
def add_column(board_name, column_title):
	"""Adds new column to Kanban Board"""
	doc = finergy.get_doc("Kanban Board", board_name)
	for col in doc.columns:
		if column_title == col.column_name:
			finergy.throw(_("Column <b>{0}</b> already exist.").format(column_title))

	doc.append("columns", dict(column_name=column_title))
	doc.save()
	return doc.columns


@finergy.whitelist()
def archive_restore_column(board_name, column_title, status):
	"""Set column's status to status"""
	doc = finergy.get_doc("Kanban Board", board_name)
	for col in doc.columns:
		if column_title == col.column_name:
			col.status = status

	doc.save()
	return doc.columns


@finergy.whitelist()
def update_order(board_name, order):
	"""Save the order of cards in columns"""
	board = finergy.get_doc("Kanban Board", board_name)
	doctype = board.reference_doctype
	fieldname = board.field_name
	order_dict = json.loads(order)

	updated_cards = []
	for col_name, cards in iteritems(order_dict):
		for card in cards:
			column = finergy.get_value(doctype, {"name": card}, fieldname)
			if column != col_name:
				finergy.set_value(doctype, card, fieldname, col_name)
				updated_cards.append(dict(name=card, column=col_name))

		for column in board.columns:
			if column.column_name == col_name:
				column.order = json.dumps(cards)

	board.save()
	return board, updated_cards


@finergy.whitelist()
def update_order_for_single_card(
	board_name, docname, from_colname, to_colname, old_index, new_index
):
	"""Save the order of cards in columns"""
	board = finergy.get_doc("Kanban Board", board_name)
	doctype = board.reference_doctype
	fieldname = board.field_name
	old_index = finergy.parse_json(old_index)
	new_index = finergy.parse_json(new_index)

	# save current order and index of columns to be updated
	from_col_order, from_col_idx = get_kanban_column_order_and_index(board, from_colname)
	to_col_order, to_col_idx = get_kanban_column_order_and_index(board, to_colname)

	if from_colname == to_colname:
		from_col_order = to_col_order

	to_col_order.insert(new_index, from_col_order.pop((old_index)))

	# save updated order
	board.columns[from_col_idx].order = finergy.as_json(from_col_order)
	board.columns[to_col_idx].order = finergy.as_json(to_col_order)
	board.save()

	# update changed value in doc
	finergy.set_value(doctype, docname, fieldname, to_colname)

	return board


def get_kanban_column_order_and_index(board, colname):
	for i, col in enumerate(board.columns):
		if col.column_name == colname:
			col_order = finergy.parse_json(col.order)
			col_idx = i

	return col_order, col_idx


@finergy.whitelist()
def add_card(board_name, docname, colname):
	board = finergy.get_doc("Kanban Board", board_name)

	col_order, col_idx = get_kanban_column_order_and_index(board, colname)
	col_order.insert(0, docname)

	board.columns[col_idx].order = finergy.as_json(col_order)

	board.save()
	return board


@finergy.whitelist()
def quick_kanban_board(doctype, board_name, field_name, project=None):
	"""Create new KanbanBoard quickly with default options"""

	doc = finergy.new_doc("Kanban Board")
	meta = finergy.get_meta(doctype)

	doc.kanban_board_name = board_name
	doc.reference_doctype = doctype
	doc.field_name = field_name

	if project:
		doc.filters = '[["Task","project","=","{0}"]]'.format(project)

	options = ""
	for field in meta.fields:
		if field.fieldname == field_name:
			options = field.options

	columns = []
	if options:
		columns = options.split("\n")

	for column in columns:
		if not column:
			continue
		doc.append("columns", dict(column_name=column))

	if doctype in ["Note", "ToDo"]:
		doc.private = 1

	doc.save()
	return doc


def get_order_for_column(board, colname):
	filters = [[board.reference_doctype, board.field_name, "=", colname]]
	if board.filters:
		filters.append(finergy.parse_json(board.filters)[0])

	return finergy.as_json(finergy.get_list(board.reference_doctype, filters=filters, pluck="name"))


@finergy.whitelist()
def update_column_order(board_name, order):
	"""Set the order of columns in Kanban Board"""
	board = finergy.get_doc("Kanban Board", board_name)
	order = json.loads(order)
	old_columns = board.columns
	new_columns = []

	for col in order:
		for column in old_columns:
			if col == column.column_name:
				new_columns.append(column)
				old_columns.remove(column)

	new_columns.extend(old_columns)

	board.columns = []
	for col in new_columns:
		board.append(
			"columns",
			dict(
				column_name=col.column_name,
				status=col.status,
				order=col.order,
				indicator=col.indicator,
			),
		)

	board.save()
	return board


@finergy.whitelist()
def set_indicator(board_name, column_name, indicator):
	"""Set the indicator color of column"""
	board = finergy.get_doc("Kanban Board", board_name)

	for column in board.columns:
		if column.column_name == column_name:
			column.indicator = indicator

	board.save()
	return board


@finergy.whitelist()
def save_filters(board_name, filters):
	"""Save filters silently"""
	finergy.db.set_value("Kanban Board", board_name, "filters", filters, update_modified=False)


@finergy.whitelist()
def save_settings(board_name: str, settings: str) -> Document:
	settings = json.loads(settings)
	doc = finergy.get_doc("Kanban Board", board_name)

	fields = settings["fields"]
	if not isinstance(fields, str):
		fields = json.dumps(fields)

	doc.fields = fields
	doc.show_labels = settings["show_labels"]
	doc.save()

	resp = doc.as_dict()
	resp["fields"] = finergy.parse_json(resp["fields"])

	return resp
