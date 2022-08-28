# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	finergy.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	finergy.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	finergy.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
