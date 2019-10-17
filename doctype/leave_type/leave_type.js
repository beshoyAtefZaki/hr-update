frappe.ui.form.on("Leave Type", {
	refresh: function(frm) {
		frm.add_custom_button(__("Allocations"), function() {
			frappe.set_route("List", "Leave Allocation",
			{"leave_type": frm.doc.name});
		});
	},

	is_lwp:function(frm){
		if(frm.doc.is_lwp=='1')
		{
			if(parseFloat(frm.doc.payroll_ratio) > 0)
			{
				frm.set_value('payroll_ratio',0);
			}
		}
		else
		{
			if(parseFloat(frm.doc.payroll_ratio) == 0)
			{
				frm.set_value('payroll_ratio',100);
			}
		}
	}

});
