# Copyright (c) 2020, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import finergy


def execute():
	if finergy.db.exists("DocType", "Onboarding"):
		finergy.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
