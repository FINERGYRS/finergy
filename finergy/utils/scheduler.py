# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# MIT License. See license.txt
"""
Events:
	always
	daily
	monthly
	weekly
"""
# imports - compatibility imports
from __future__ import print_function, unicode_literals

# imports - standard imports
import os
import time

# imports - third party imports
import schedule

# imports - module imports
import finergy
from finergy.core.doctype.user.user import STANDARD_USERS
from finergy.installer import update_site_config
from finergy.utils import get_sites, now_datetime
from finergy.utils.background_jobs import get_jobs

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def start_scheduler():
	"""Run enqueue_events_for_all_sites every 2 minutes (default).
	Specify scheduler_interval in seconds in common_site_config.json"""

	schedule.every(finergy.get_conf().scheduler_tick_interval or 60).seconds.do(
		enqueue_events_for_all_sites
	)

	while True:
		schedule.run_pending()
		time.sleep(1)


def enqueue_events_for_all_sites():
	"""Loop through sites and enqueue events that are not already queued"""

	if os.path.exists(os.path.join(".", ".restarting")):
		# Don't add task to queue if webserver is in restart mode
		return

	with finergy.init_site():
		sites = get_sites()

	for site in sites:
		try:
			enqueue_events_for_site(site=site)
		except Exception as e:
			print(e.__class__, "Failed to enqueue events for site: {}".format(site))


def enqueue_events_for_site(site):
	def log_and_raise():
		error_message = "Exception in Enqueue Events for Site {0}\n{1}".format(
			site, finergy.get_traceback()
		)
		finergy.logger("scheduler").error(error_message)

	try:
		finergy.init(site=site)
		finergy.connect()
		if is_scheduler_inactive():
			return

		enqueue_events(site=site)

		finergy.logger("scheduler").debug("Queued events for site {0}".format(site))
	except finergy.db.OperationalError as e:
		if finergy.db.is_access_denied(e):
			finergy.logger("scheduler").debug("Access denied for site {0}".format(site))
		else:
			log_and_raise()
	except Exception:
		log_and_raise()

	finally:
		finergy.destroy()


def enqueue_events(site):
	if schedule_jobs_based_on_activity():
		finergy.flags.enqueued_jobs = []
		queued_jobs = get_jobs(site=site, key="job_type").get(site) or []
		for job_type in finergy.get_all("Scheduled Job Type", ("name", "method"), dict(stopped=0)):
			if not job_type.method in queued_jobs:
				# don't add it to queue if still pending
				finergy.get_doc("Scheduled Job Type", job_type.name).enqueue()


def is_scheduler_inactive():
	if finergy.local.conf.maintenance_mode:
		return True

	if finergy.local.conf.pause_scheduler:
		return True

	if is_scheduler_disabled():
		return True

	return False


def is_scheduler_disabled():
	if finergy.conf.disable_scheduler:
		return True

	return not finergy.utils.cint(finergy.db.get_single_value("System Settings", "enable_scheduler"))


def toggle_scheduler(enable):
	finergy.db.set_value("System Settings", None, "enable_scheduler", 1 if enable else 0)


def enable_scheduler():
	toggle_scheduler(True)


def disable_scheduler():
	toggle_scheduler(False)


def schedule_jobs_based_on_activity(check_time=None):
	"""Returns True for active sites defined by Activity Log
	Returns True for inactive sites once in 24 hours"""
	if is_dormant(check_time=check_time):
		# ensure last job is one day old
		last_job_timestamp = finergy.db.get_last_created("Scheduled Job Log")
		if not last_job_timestamp:
			return True
		else:
			if ((check_time or now_datetime()) - last_job_timestamp).total_seconds() >= 86400:
				# one day is passed since jobs are run, so lets do this
				return True
			else:
				# schedulers run in the last 24 hours, do nothing
				return False
	else:
		# site active, lets run the jobs
		return True


def is_dormant(check_time=None):
	last_activity_log_timestamp = finergy.db.get_last_created("Activity Log")
	since = (finergy.get_system_settings("dormant_days") or 4) * 86400
	if not last_activity_log_timestamp:
		return True
	if ((check_time or now_datetime()) - last_activity_log_timestamp).total_seconds() >= since:
		return True
	return False


@finergy.whitelist()
def activate_scheduler():
	if is_scheduler_disabled():
		enable_scheduler()
	if finergy.conf.pause_scheduler:
		update_site_config("pause_scheduler", 0)
