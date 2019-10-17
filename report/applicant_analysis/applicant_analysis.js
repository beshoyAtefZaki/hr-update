// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Applicant Analysis"] = {
	"filters": [
		{
			"fieldname": "Job Opening",
			"label": __("Job Opening"),
			"fieldtype": "Link",
			"options": "Job Opening"
		},
		{
			"fieldname": "Skills",
			"label": __("Skills"),
			"fieldtype": "Link",
			"options": "Skills",
			"get_query": function () {
				return {
					"doctype": "Skills",
					"filters": {
						"parenttype": "Designation",
					}
				}
		}
	}
	]
}
