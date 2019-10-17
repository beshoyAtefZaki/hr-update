// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Position Vacancies"] = {
	"filters": [
		{
			"fieldname": "designation",
			"label": __("Designation"),
			"fieldtype": "Link",
			"options": "Designation"
		},
		{
			"fieldname": "Position",
			"label": __("Position"),
			"fieldtype": "Data",
		},
		{
			"fieldname": "Department",
			"label": __("Department"),
			"fieldtype": "Link",
			"options": "Department"
		},
		{
			"fieldname": "Status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": "Active\nInactive"
		}
	]
}
