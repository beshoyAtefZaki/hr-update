// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Insurance Report"] = {
	"filters": [
		{
		"fieldname": "start_date",
		"label": __("Month"),
		"fieldtype": "Select",
		"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
		"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
		"Dec"][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
		}
		// ,
		// {
		// 	"fieldname": "Department",
		// 	"label": __("Department"),
		// 	"fieldtype": "Link",
		// 	"options": "Department"
		// }
		// ,
		// {
		// 	"fieldname": "salary_component",
		// 	"label": __("salary_component"),
		// 	"fieldtype": "Link",
		// 	"options": "Salary Component"
		// }
	]
}
