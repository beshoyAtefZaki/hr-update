// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Extend the test period', {
	refresh: function(frm) {

	},
	employee:function (frm) {
		frappe.call({
				method:"erpnext.hr.doctype.resignation.resignation.get_employee_date",
				args: {
					employee_name:frm.doc.employee
				},
			callback:function (r) {
					frappe.show_alert(r.message);
					var format = str_format(frm.fields_dict.template_html.wrapper.outerHTML,[])
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