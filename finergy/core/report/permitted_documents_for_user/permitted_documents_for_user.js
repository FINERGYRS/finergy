// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.query_reports["Permitted Documents For User"] = {
	"filters": [
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User",
			"reqd": 1
		},
		{
			"fieldname": "doctype",
			"label": __("DocType"),
			"fieldtype": "Link",
			"options": "DocType",
			"reqd": 1,
			"get_query": function () {
				return {
					"query": "finergy.core.report.permitted_documents_for_user.permitted_documents_for_user.query_doctypes",
					"filters": {
						"user": finergy.query_report.get_filter_value('user')
					}
				}
			}
		},
		{
			"fieldname": "show_permissions",
			"label": __("Show Permissions"),
			"fieldtype": "Check"
		}
	]
}
