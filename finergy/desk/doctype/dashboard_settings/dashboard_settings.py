# -*- coding: utf-8 -*-
# Copyright (c) 2020, Finergy Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import finergy

# import finergy
from finergy.model.document import Document


class DashboardSettings(Document):
	pass


@finergy.whitelist()
def create_dashboard_settings(user):
	if not finergy.db.exists("Dashboard Settings", user):
		doc = finergy.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		finergy.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = finergy.session.user

	return """(`tabDashboard Settings`.name = {user})""".format(user=finergy.db.escape(user))


@finergy.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = finergy.parse_json(reset)
	doc = finergy.get_doc("Dashboard Settings", finergy.session.user)
	chart_config = finergy.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = finergy.parse_json(config)
		if not chart_name in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	finergy.db.set_value(
		"Dashboard Settings", finergy.session.user, "chart_config", json.dumps(chart_config)
	)
