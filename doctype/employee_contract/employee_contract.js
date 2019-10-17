// Copyright (c) 2019, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
// cutomization
frappe.ui.form.on('Employee Contract', {


	refresh: function(frm) {
		var now_day = frappe.datetime.add_days(frappe.datetime.get_today(),10)
		var end_date = frm.doc.contract_end_date
		if (now_day < end_date){
			console.log(now_day)
		}
	} ,
	//
	citizen_or_resident: function(frm) {
		var cit_or_res = frm.doc.citizen_or_resident  ;
		if (cit_or_res == "Citizen"){
			frm.set_value("nationality" ,"Saudi") ;
		}
	} ,
	// clear start date when user add duration
	duration_of_the_contract: function(frm) {
		// var today =frappe.utils.nowdate() ;

		frm.set_value("contract_strat_date" ,"") ;
	} ,
	// add end date to contract
	contract_strat_date: function(frm) {
		var duration_of_contract = frm.doc.duration_of_the_contract ;
		var monthes = 0 ;
		if (! duration_of_contract) {
			frappe.msgprint(" You shoud add duration to the Contract")
		}
		else{
			if (duration_of_contract == "6 أشهر"){
				monthes = 6 ;

			}
			if (duration_of_contract == "عام"){
				monthes = 12 ;

			}
			if (duration_of_contract == "عامان"){
				monthes = 24 ;

			}
			if (duration_of_contract =="ثلاثة أعوام"){
				monthes = 36 ;

			}
		var contract_end_date = frappe.datetime.add_days(
										frappe.datetime.add_months(frm.doc.contract_strat_date,  monthes), -1);
		frm.set_value("contract_end_date" ,contract_end_date) ;
		}

	} ,
});
