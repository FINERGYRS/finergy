from __future__ import unicode_literals

import json

import finergy
from finergy.config import get_modules_from_all_apps_for_user
from finergy.desk.moduleview import get_onboard_items


def execute():
	"""Reset the initial customizations for desk, with modules, indices and links."""
	finergy.reload_doc("core", "doctype", "user")
	finergy.db.sql("""update tabUser set home_settings = ''""")
