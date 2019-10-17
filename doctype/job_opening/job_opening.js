// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Job Opening", {
    onload: function () {
        cur_frm.set_query("position", function () {
            return {
                query: "erpnext.hr.doctype.employee.employee.get_unused_position"
            };
        });
    },
    publish: function(frm) {
		frm.toggle_reqd("publish_date", frm.doc.publish ? 1 : 0);
	}
});
