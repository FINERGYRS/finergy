# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import json
import os
import sys

import finergy
import finergy.model.sync
import finergy.modules.patch_handler
import finergy.translate
from finergy.cache_manager import clear_global_cache
from finergy.core.doctype.language.language import sync_languages
from finergy.core.doctype.scheduled_job_type.scheduled_job_type import sync_jobs
from finergy.database.schema import add_column
from finergy.desk.notifications import clear_notifications
from finergy.modules.utils import sync_customizations
from finergy.search.website_search import build_index_for_all_routes
from finergy.utils.connections import check_connection
from finergy.utils.dashboard import sync_dashboards
from finergy.utils.fixtures import sync_fixtures
from finergy.website import render


def migrate(verbose=True, skip_failing=False, skip_search_index=False):
	"""Migrate all apps to the current version, will:
	- run before migrate hooks
	- run patches
	- sync doctypes (schema)
	- sync dashboards
	- sync fixtures
	- sync desktop icons
	- sync web pages (from /www)
	- sync web pages (from /www)
	- run after migrate hooks
	"""

	service_status = check_connection(redis_services=["redis_cache"])
	if False in service_status.values():
		for service in service_status:
			if not service_status.get(service, True):
				print("{} service is not running.".format(service))
		print(
			"""Cannot run bench migrate without the services running.
If you are running bench in development mode, make sure that bench is running:

$ bench start

Otherwise, check the server logs and ensure that all the required services are running."""
		)
		sys.exit(1)

	touched_tables_file = finergy.get_site_path("touched_tables.json")
	if os.path.exists(touched_tables_file):
		os.remove(touched_tables_file)

	finergy.flags.touched_tables = set()

	try:
		add_column(doctype="DocType", column_name="migration_hash", fieldtype="Data")
		finergy.flags.in_migrate = True

		clear_global_cache()

		# run before_migrate hooks
		for app in finergy.get_installed_apps():
			for fn in finergy.get_hooks("before_migrate", app_name=app):
				finergy.get_attr(fn)()

		# run patches
		finergy.modules.patch_handler.run_all(skip_failing)

		# sync
		finergy.model.sync.sync_all(verbose=verbose)
		finergy.translate.clear_cache()
		sync_jobs()
		sync_fixtures()
		sync_dashboards()
		sync_customizations()
		sync_languages()

		finergy.get_doc("Portal Settings", "Portal Settings").sync_menu()

		# syncs statics
		render.clear_cache()

		# updating installed applications data
		finergy.get_single("Installed Applications").update_versions()

		# run after_migrate hooks
		for app in finergy.get_installed_apps():
			for fn in finergy.get_hooks("after_migrate", app_name=app):
				finergy.get_attr(fn)()

		# build web_routes index
		if not skip_search_index:
			# Run this last as it updates the current session
			print("Building search index for {}".format(finergy.local.site))
			build_index_for_all_routes()

		finergy.db.commit()

		clear_notifications()

		finergy.publish_realtime("version-update")
		finergy.flags.in_migrate = False
	finally:
		with open(touched_tables_file, "w") as f:
			json.dump(list(finergy.flags.touched_tables), f, sort_keys=True, indent=4)
		finergy.flags.touched_tables.clear()
