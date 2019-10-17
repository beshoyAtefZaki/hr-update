// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
cur_frm.add_fetch('employee','employment_type','employment_type');

frappe.ui.form.on('Transfer Employee', {
	refresh: function(frm) {

	},
	employee: function(frm) {
		frm.set_query("transfer_to", function(){
        return {
            "filters": [["employee_type_name", "!=", cur_frm.doc.employment_type]]
        }
    });
}

});


