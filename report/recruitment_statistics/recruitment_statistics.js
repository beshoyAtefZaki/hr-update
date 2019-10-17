// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Recruitment Statistics"] = {
	"filters": [
			{
			"fieldname": "JobTitle",
			"label": __("Job"),
			"fieldtype": "Link",
			"options": "Job Opening"
		}
	]
}
