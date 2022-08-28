# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finergy Technologies and contributors
# For license information, please see license.txt


from __future__ import unicode_literals

import json

import finergy
from finergy.desk.form.load import get_attachments
from finergy.desk.query_report import generate_report_result
from finergy.model.document import Document
from finergy.utils import gzip_compress, gzip_decompress
from finergy.utils.background_jobs import enqueue


class PreparedReport(Document):
	def before_insert(self):
		self.status = "Queued"
		self.report_start_time = finergy.utils.now()

	def enqueue_report(self):
		enqueue(run_background, prepared_report=self.name, timeout=6000)


def run_background(prepared_report):
	instance = finergy.get_doc("Prepared Report", prepared_report)
	report = finergy.get_doc("Report", instance.ref_report_doctype)

	try:
		report.custom_columns = []

		if report.report_type == "Custom Report":
			custom_report_doc = report
			reference_report = custom_report_doc.reference_report
			report = finergy.get_doc("Report", reference_report)
			if custom_report_doc.json:
				data = json.loads(custom_report_doc.json)
				if data:
					report.custom_columns = data["columns"]

		result = generate_report_result(report=report, filters=instance.filters, user=instance.owner)
		create_json_gz_file(result["result"], "Prepared Report", instance.name)

		instance.status = "Completed"
		instance.columns = json.dumps(result["columns"])
		instance.report_end_time = finergy.utils.now()
		instance.save(ignore_permissions=True)

	except Exception:
		finergy.log_error(finergy.get_traceback())
		instance = finergy.get_doc("Prepared Report", prepared_report)
		instance.status = "Error"
		instance.error_message = finergy.get_traceback()
		instance.save(ignore_permissions=True)

	finergy.publish_realtime(
		"report_generated",
		{"report_name": instance.report_name, "name": instance.name},
		user=finergy.session.user,
	)


@finergy.whitelist()
def get_reports_in_queued_state(report_name, filters):
	reports = finergy.get_all(
		"Prepared Report",
		filters={
			"report_name": report_name,
			"filters": json.dumps(json.loads(filters)),
			"status": "Queued",
		},
	)
	return reports


def delete_expired_prepared_reports():
	system_settings = finergy.get_single("System Settings")
	enable_auto_deletion = system_settings.enable_prepared_report_auto_deletion
	if enable_auto_deletion:
		expiry_period = system_settings.prepared_report_expiry_period
		prepared_reports_to_delete = finergy.get_all(
			"Prepared Report",
			filters={"creation": ["<", finergy.utils.add_days(finergy.utils.now(), -expiry_period)]},
		)

		batches = finergy.utils.create_batch(prepared_reports_to_delete, 100)
		for batch in batches:
			args = {
				"reports": batch,
			}
			enqueue(method=delete_prepared_reports, job_name="delete_prepared_reports", **args)


@finergy.whitelist()
def delete_prepared_reports(reports):
	reports = finergy.parse_json(reports)
	for report in reports:
		finergy.delete_doc(
			"Prepared Report", report["name"], ignore_permissions=True, delete_permanently=True
		)


def create_json_gz_file(data, dt, dn):
	# Storing data in CSV file causes information loss
	# Reports like P&L Statement were completely unsuable because of this
	json_filename = "{0}.json.gz".format(
		finergy.utils.data.format_datetime(finergy.utils.now(), "Y-m-d-H:M")
	)
	encoded_content = finergy.safe_encode(finergy.as_json(data))
	compressed_content = gzip_compress(encoded_content)

	# Call save() file function to upload and attach the file
	_file = finergy.get_doc(
		{
			"doctype": "File",
			"file_name": json_filename,
			"attached_to_doctype": dt,
			"attached_to_name": dn,
			"content": compressed_content,
			"is_private": 1,
		}
	)
	_file.save(ignore_permissions=True)


@finergy.whitelist()
def download_attachment(dn):
	attachment = get_attachments("Prepared Report", dn)[0]
	finergy.local.response.filename = attachment.file_name[:-2]
	attached_file = finergy.get_doc("File", attachment.name)
	finergy.local.response.filecontent = gzip_decompress(attached_file.get_content())
	finergy.local.response.type = "binary"


def get_permission_query_condition(user):
	if not user:
		user = finergy.session.user
	if user == "Administrator":
		return None

	from finergy.utils.user import UserPermissions

	user = UserPermissions(user)

	if "System Manager" in user.roles:
		return None

	reports = [finergy.db.escape(report) for report in user.get_all_reports().keys()]

	return """`tabPrepared Report`.ref_report_doctype in ({reports})""".format(
		reports=",".join(reports)
	)


def has_permission(doc, user):
	if not user:
		user = finergy.session.user
	if user == "Administrator":
		return True

	from finergy.utils.user import UserPermissions

	user = UserPermissions(user)

	if "System Manager" in user.roles:
		return True

	return doc.ref_report_doctype in user.get_all_reports().keys()
