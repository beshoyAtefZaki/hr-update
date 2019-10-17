// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Interview Invitation', {
	refresh: function(frm) {

		if(!frm.doc.__islocal && (frm.doc.docstatus === 1)&& frm.doc.__onload) {

			frm.add_custom_button(__("Interview Evaluation"), function() {
					frappe.set_route("Form", "Interview Evaluation", frm.doc.__onload.interview_evaluation);
				}, __("View"));

		}else if (!frm.doc.__islocal && (frm.doc.docstatus === 1)){
			frm.add_custom_button(__("Interview Evaluation"), function() {
						frappe.route_options = {
							"applicant_name": frm.doc.job_applicant,
							"interview_invitation" :frm.doc.name,
						};
						frappe.new_doc("Interview Evaluation");
				}, __("Make"));

		}

	},
	onload:function (frm) {
		 frm.set_query("interviewer_name","interviewers",  function() {
			return {
				query: "erpnext.hr.doctype.interview_invitation.interview_invitation.get_interviewers"
			};
		 });

	},
	onload_post_render: function(frm) {
		frm.get_field("interviewers").grid.set_multiple_add("interviewer_name");
	}

});
