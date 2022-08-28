# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json

import finergy


@finergy.whitelist()
def update_task(args, field_map):
	"""Updates Doc (called via gantt) based on passed `field_map`"""
	args = finergy._dict(json.loads(args))
	field_map = finergy._dict(json.loads(field_map))
	d = finergy.get_doc(args.doctype, args.name)
	d.set(field_map.start, args.start)
	d.set(field_map.end, args.end)
	d.save()
