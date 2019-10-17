// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Hiring Request', {
	basic_salary: function(frm) {
		calculate_total_package(frm.doc)
	},
	housing_allowance: function(frm) {
		calculate_total_package(frm.doc)
	},
	transportation_allowance: function(frm) {
		calculate_total_package(frm.doc)
	},
	other_allowance: function(frm) {
		calculate_total_package(frm.doc)
	},

	designation: function(frm) {
		if (frm.doc.designation){
			frappe.model.with_doc("Designation", frm.doc.designation, function() {
			frm.clear_table('responsibilities', []);
			frm.refresh_field("responsibilities");
            var tabletransfer= frappe.model.get_doc("Designation", frm.doc.designation);
            $.each(tabletransfer.responsibilities, function(index, row){
                d = frm.add_child("responsibilities");
                d.duty = row.duty;
                frm.refresh_field("responsibilities");
            });

        });
		}


	}
});


var calculate_total_package = function(doc) {
	doc.gross_pay = flt(doc.basic_salary) + flt(doc.housing_allowance)+ flt(doc.transportation_allowance)+flt(doc.other_allowance);
	doc.total_package = Math.round(doc.gross_pay);
	refresh_field('total_package');
}