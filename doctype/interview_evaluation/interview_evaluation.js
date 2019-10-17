// Copyright (c) 2017, Ebkar Technology & Management Solutions and contributors
// For license information, please see license.txt


cur_frm.add_fetch('applicant_name', 'designation', 'job_designation');
cur_frm.add_fetch('applicant_name', 'expected_salary', 'job_salary');

frappe.ui.form.on('Interview Evaluation', {
	refresh: function(frm) {

	if ((!frm.doc.__islocal) && (frm.doc.is_recommended_applicant == 'Yes') && (frm.doc.docstatus === 1)) {

			frm.add_custom_button(__("Offer Letter"), function() {
					frappe.route_options = {
						"job_applicant": frm.doc.applicant_name,
						"applicant_name": frm.doc.applicant_name,
					};
					frappe.new_doc("Offer Letter");
				});
		}

	},

	before_submit: function(frm){
		frm.toggle_reqd('is_recommended_applicant', true);
	},
	onload: function(frm){
		var tabletransfer= frappe.model.get_list('Interviewers', {'parent': frm.doc.interview_invitation});

		 $.each(tabletransfer, function(index, row){
            d = frm.add_child("interviewers");
            d.interviewer_name = row.interviewer_name;
            d.attendance = row.attendance;
            frm.refresh_field("interviewers");
        });

		cur_frm.set_query("applicant_name", function() {
			return {
				filters: [
					["status", "!=", 'Rejected']
				]
			}
		});

		cur_frm.set_query("question","questions",  function() {
			return {
				filters: [
					["designation", "=", cur_frm.doc.job_designation]
				]
			};
		});


	},
	applicant_name : function(frm) {

		cur_frm.set_value('range_of_salary_expectations', cur_frm.doc.job_salary);

	}


});
