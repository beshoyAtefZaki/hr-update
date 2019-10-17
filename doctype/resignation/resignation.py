# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from dateutil import relativedelta
from frappe import msgprint , _
from frappe.model.document import Document

class Resignation(Document):
	pass

@frappe.whitelist()
def get_employee_date(employee_name=None):

	current_period = frappe._dict()
	if employee_name != None:
		current_period = frappe.db.sql(
			"""
				select 
						date_of_joining, CURDATE() to_day
					from tabEmployee 
						where (employee = %s or employee_name = %s)
			""", (employee_name,employee_name),as_dict=1, debug=False)[0]
		
		current_period.update(date_difference(current_period['to_day'],current_period['date_of_joining']))
		
		last_period = frappe._dict()
		data = frappe.db.sql(
			"""
				select sum(ifnull(DATEDIFF(to_date,from_date),0)) T_days
					from `tabEmployee Internal Work History` 
						where parent = (select employee from tabEmployee where employee_name= %s)
			""", (employee_name),as_dict=1, debug=False)[0]
		
		
		last_period = convert_days_to_year_month_days(int(data['T_days']  or "0"))
		total_period = get_total_period(current_period,last_period)
			
		current_period.update(last_period)
		current_period.update(total_period)

	return current_period

@frappe.whitelist()
def date_difference(date_1,date_2):	
	data = frappe._dict()
	#This will find the difference between the two dates
	difference = relativedelta.relativedelta(date_1, date_2)
	
	years = difference.years
	months = difference.months
	days = difference.days
	
	data['years'] = years
	data['months'] = months
	data['days'] = days
	
	return data

@frappe.whitelist()
def convert_days_to_year_month_days(total_days):
	data = frappe._dict()
	
	data['total_days'] = total_days % 30
	
	data['total_months'] = (total_days / 30 ) % 12 
	
	data['total_years'] = (total_days / 30 ) / 12
	
	return data

@frappe.whitelist()
def get_total_period(current_period,last_period):
	total_period = frappe._dict()
	
	total_period['total_period_days']   = current_period.days + last_period.total_days
	total_period['total_period_months'] = current_period.months + last_period.total_months
	total_period['total_period_years']  = current_period.years + last_period.total_years
	
	if (int(total_period['total_period_days']) > 30):
		total_period['total_period_days'] -=  30 
		total_period['total_period_months'] += 1
		
	if (int(total_period['total_period_months']) > 12):
		total_period['total_period_months'] -= 12
		total_period['total_period_years']  += 1	
	
	return total_period





