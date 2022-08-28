# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy

sitemap = 1


def get_context(context):
	context.doc = finergy.get_doc("About Us Settings", "About Us Settings")

	return context
