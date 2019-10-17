// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Get Users', {
	refresh: function(frm) {
	frm.disable_save();
		frm.add_custom_button(__("Get Users"), function () {
		// When this button is clicked, do this
			var d = frm.doc;
			frappe.call({
				method: "erpnext.hr.doctype.get_users.get_users.Get_device_Users",
				args: {
					doc: frm.doc
				},
				callback: function (r) {
					//if(r.message == "item not in table"){
					var new_row = frm.add_child("ATT Users");
					new_row.uid = d.uid;
					new_row.name1 = d.name;
					new_row.privilege = d.privilege;
					new_row.password = d.password;
					new_row.group_id = d.group_id;
					new_row.user_id = d.user_id;
					//}
				}
			});
			refresh_field("ATT Users")

		})
	}
});

