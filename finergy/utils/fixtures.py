# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

import os

import finergy
from finergy.core.doctype.data_import.data_import import export_json, import_doc


def sync_fixtures(app=None):
	"""Import, overwrite fixtures from `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = finergy.get_installed_apps()

	finergy.flags.in_fixtures = True

	for app in apps:
		fixtures_path = finergy.get_app_path(app, "fixtures")
		if os.path.exists(fixtures_path):
			import_doc(fixtures_path)

		import_custom_scripts(app)

	finergy.flags.in_fixtures = False

	finergy.db.commit()


def import_custom_scripts(app):
	"""Import custom scripts from `[app]/fixtures/custom_scripts`"""
	if os.path.exists(finergy.get_app_path(app, "fixtures", "custom_scripts")):
		for fname in os.listdir(finergy.get_app_path(app, "fixtures", "custom_scripts")):
			if fname.endswith(".js"):
				with open(finergy.get_app_path(app, "fixtures", "custom_scripts") + os.path.sep + fname) as f:
					doctype = fname.rsplit(".", 1)[0]
					script = f.read()
					if finergy.db.exists("Client Script", {"dt": doctype}):
						custom_script = finergy.get_doc("Client Script", {"dt": doctype})
						custom_script.script = script
						custom_script.save()
					else:
						finergy.get_doc({"doctype": "Client Script", "dt": doctype, "script": script}).insert()


def export_fixtures(app=None):
	"""Export fixtures as JSON to `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = finergy.get_installed_apps()
	for app in apps:
		for fixture in finergy.get_hooks("fixtures", app_name=app):
			filters = None
			or_filters = None
			if isinstance(fixture, dict):
				filters = fixture.get("filters")
				or_filters = fixture.get("or_filters")
				fixture = fixture.get("doctype") or fixture.get("dt")
			print(
				"Exporting {0} app {1} filters {2}".format(fixture, app, (filters if filters else or_filters))
			)
			if not os.path.exists(finergy.get_app_path(app, "fixtures")):
				os.mkdir(finergy.get_app_path(app, "fixtures"))

			export_json(
				fixture,
				finergy.get_app_path(app, "fixtures", finergy.scrub(fixture) + ".json"),
				filters=filters,
				or_filters=or_filters,
				order_by="idx asc, creation asc",
			)
