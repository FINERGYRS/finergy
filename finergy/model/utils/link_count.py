# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

from six import iteritems

import finergy

ignore_doctypes = ("DocType", "Print Format", "Role", "Module Def", "Communication", "ToDo")


def notify_link_count(doctype, name):
	"""updates link count for given document"""
	if hasattr(finergy.local, "link_count"):
		if (doctype, name) in finergy.local.link_count:
			finergy.local.link_count[(doctype, name)] += 1
		else:
			finergy.local.link_count[(doctype, name)] = 1


def flush_local_link_count():
	"""flush from local before ending request"""
	if not getattr(finergy.local, "link_count", None):
		return

	link_count = finergy.cache().get_value("_link_count")
	if not link_count:
		link_count = {}

		for key, value in finergy.local.link_count.items():
			if key in link_count:
				link_count[key] += finergy.local.link_count[key]
			else:
				link_count[key] = finergy.local.link_count[key]

	finergy.cache().set_value("_link_count", link_count)


def update_link_count():
	"""increment link count in the `idx` column for the given document"""
	link_count = finergy.cache().get_value("_link_count")

	if link_count:
		for key, count in iteritems(link_count):
			if key[0] not in ignore_doctypes:
				try:
					finergy.db.sql(
						"update `tab{0}` set idx = idx + {1} where name=%s".format(key[0], count),
						key[1],
						auto_commit=1,
					)
				except Exception as e:
					if not finergy.db.is_table_missing(e):  # table not found, single
						raise e
	# reset the count
	finergy.cache().delete_value("_link_count")
