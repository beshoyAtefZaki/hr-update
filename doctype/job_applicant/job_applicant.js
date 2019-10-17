// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

// For license information, please see license.txt

// for communication
cur_frm.email_field = "email_id";

frappe.ui.form.on("Job Applicant", {
	refresh: function(frm) {
		if (!frm.doc.__islocal) {
			if (frm.doc.__onload && frm.doc.__onload.offer_letter) {
				frm.add_custom_button(__("Offer Letter"), function() {
					frappe.set_route("Form", "Offer Letter", frm.doc.__onload.offer_letter);
				}, __("View"));
			}
			if (frm.doc.__onload  && frm.doc.__onload.interview_invitation) {
				frm.add_custom_button(__("Interview Invitation"), function() {
					frappe.set_route("Form", "Interview Invitation", frm.doc.__onload.interview_invitation);
				}, __("View"));

			} else {
				frm.add_custom_button(__("Interview Invitation"), function() {
					frappe.route_options = {
						"job_applicant": frm.doc.name,
						"applicant_name": frm.doc.applicant_name,
					};
					frappe.new_doc("Interview Invitation");
				}, __("Make"));

				cur_frm.page.set_inner_btn_group_as_primary(__("Make"));
			}
		}

	}
});
cur_frm.set_query("skill", "skills", function(doc) {
			return {
				query:"",
				filters:{
					parent: cur_frm.doc.designation
				}
			}
});
