# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.delete_doc_if_exists("DocType", "User Permission for Page and Report")
