# Copyright (c) 2022, Finergy and Contributors
# License: MIT. See LICENSE


import finergy
from finergy.model import data_field_options


def execute():
	custom_field = finergy.qb.DocType("Custom Field")
	(
		finergy.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
