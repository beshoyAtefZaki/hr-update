// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Salary cheet"] = {
	"filters": [
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee",
			"reqd": 1
		},
	] ,onload:function(report){
		report.page.add_inner_button(__("Test") , function(){
			// frappe.call({
			// 	"method": "erpnext.hr.report.salary_cheet.get_name",
			// })
			frappe.msgprint(frappe.query_report_filters_by_name.employee.get_value()) ;
		})
	}

}
