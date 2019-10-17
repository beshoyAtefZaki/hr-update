// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["The pensioners"] = {
	"filters": [
		{
			"fieldname": "Employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"gender",
			"label":"Gender",
			"fieldtype":"Select",
			"options":"Male\nFemale"
		},
		{
			"fieldname": "retire_date",
			"label": "Retire Date",
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}



	]
}
