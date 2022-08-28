# Copyright (c) 2021, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import finergy


def execute():
	"""Convert Query Report json to support other content"""
	records = finergy.get_all("Report", filters={"json": ["!=", ""]}, fields=["name", "json"])
	for record in records:
		jstr = record["json"]
		data = json.loads(jstr)
		if isinstance(data, list):
			# double escape braces
			jstr = f'{{"columns":{jstr}}}'
			finergy.db.update("Report", record["name"], "json", jstr)
