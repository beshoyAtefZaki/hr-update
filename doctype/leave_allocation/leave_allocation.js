// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

cur_frm.add_fetch('employee','employee_name','employee_name');
cur_frm.add_fetch('leave_type','vacation_type','vacation_type');
cur_frm.add_fetch('leave_type','default_balance','default_balance');


frappe.ui.form.on("Leave Allocation", {
	onload: function(frm) {
		if(!frm.doc.from_date) frm.set_value("from_date", frappe.datetime.get_today());

		frm.set_query("employee", function() {
			return {
				query: "erpnext.controllers.queries.employee_query"
			}
		});
		frm.set_query("leave_type", function() {
			return {
				filters: {
					is_lwp: 0
				}
			}
		})
	},

	employee: function(frm) {
		frm.trigger("calculate_total_leaves_allocated");
	},

	leave_type: function(frm) {
		frm.toggle_reqd('from_date',frm.doc.vacation_type!='Sick Vacation')
		frm.toggle_reqd('to_date',frm.doc.vacation_type!='Sick Vacation')
		frm.toggle_display('from_date',frm.doc.vacation_type!='Sick Vacation')
		frm.toggle_display('to_date',frm.doc.vacation_type!='Sick Vacation')
		frm.toggle_display('carry_forward',frm.doc.vacation_type!='Sick Vacation')
		if(frm.doc.vacation_type=='Sick Vacation'){
			frm.set_value('from_date','1900-01-01')
			frm.set_value('to_date','2199-12-31')
		}
		frm.trigger("calculate_total_leaves_allocated");

		if(frm.doc.default_balance){
			frm.set_value('new_leaves_allocated',frm.doc.default_balance);
		}else {
			frm.set_value('new_leaves_allocated',0);
		}
	},

	carry_forward: function(frm) {
		frm.trigger("calculate_total_leaves_allocated");
	},

	carry_forwarded_leaves: function(frm) {
		frm.set_value("total_leaves_allocated",
			flt(frm.doc.carry_forwarded_leaves) + flt(frm.doc.new_leaves_allocated));
	},

	new_leaves_allocated: function(frm) {
		frm.set_value("total_leaves_allocated",
			flt(frm.doc.carry_forwarded_leaves) + flt(frm.doc.new_leaves_allocated));
	},

	calculate_total_leaves_allocated: function(frm) {
		if (cint(frm.doc.carry_forward) == 1 && frm.doc.leave_type && frm.doc.employee) {
			return frappe.call({
				method: "erpnext.hr.doctype.leave_allocation.leave_allocation.get_carry_forwarded_leaves",
				args: {
					"employee": frm.doc.employee,
					"date": frm.doc.from_date,
					"leave_type": frm.doc.leave_type,
					"carry_forward": frm.doc.carry_forward
				},
				callback: function(r) {
					if (!r.exc && r.message) {
						frm.set_value('carry_forwarded_leaves', r.message);
						frm.set_value("total_leaves_allocated",
							flt(r.message) + flt(frm.doc.new_leaves_allocated));
					}
				}
			})
		} else if (cint(frm.doc.carry_forward) == 0) {
			frm.set_value("carry_forwarded_leaves", 0);
			frm.set_value("total_leaves_allocated", flt(frm.doc.new_leaves_allocated));
		}
	}
})
