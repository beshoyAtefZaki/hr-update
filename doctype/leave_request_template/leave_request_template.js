// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Leave Request Template', {
	refresh: function(frm) {
		frm.trigger("employee_name")
	},
	employee_name:function(frm){
				frappe.call({
				method: "erpnext.hr.doctype.resignation.resignation.get_employee_date",
				args: {
					employee_name:frm.doc.employee_name
				},
				callback: function(r) {
					var format = str_format(frm.fields_dict.conclusion.wrapper.outerHTML,
						[
						r.message.years,r.message.months,r.message.days,r.message.date_of_joining,
						r.message.total_years,r.message.total_months,r.message.total_days,
						r.message.total_period_years,r.message.total_period_months,r.message.total_period_days
						]);

					// cur_frm.fields_dict.conclusion.wrapper.outerHTML = format ;
					cur_frm.fields_dict.conclusion.wrapper.childNodes[0].outerHTML = format
					// frappe.show_alert(cur_frm.fields_dict.conclusion.innerHTML.elements('divcontent'));
				}
			});
	}
});

function str_format(format, args )
{
  for(var i=0; i < args.length; i++ ) {
    format = format.replace(/%s/, args[i]);
  }
  return format;
}