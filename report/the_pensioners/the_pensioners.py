# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_date(filters)

	return columns, data

def get_columns():
	columns = [
		_("Name") + ":Data:200",
		_("Employee") + ":Link/Employee:120",
		_("Date of Birth") + ":Date:100",
		_("Branch") + ":Link/Branch:120",
		_("Department") + ":Link/Department:120",
		_("Designation") + ":Link/Designation:120",
		_("Gender") + "::60",
		_("Date Of Retirement") + ":Date/Date Of Retirement:120"
	]

	return columns

def get_date(filters):
	data = []
	condition = get_condition(filters)
	data = frappe.db.sql(
		"""
			select `name`,employee_name,date_of_birth,branch,department,designation,gender,date_of_retirement
				from tabEmployee
					where status ='Active'
					%s
			;
		""" 
		% condition
            , as_list=1)

	return data

def get_condition(filters):
	conditions = ""

	if filters.get("Employee"):
		conditions += " and employee = '%s'" % \
                    filters["Employee"].replace("'", "\\'")

	if filters.get("gender"):
		conditions += " and gender = '%s'" % \
                    filters["gender"].replace("'", "\\'")

	if filters.get("retire_date"):
		conditions += " and date_of_retirement <= '%s'" % \
                    filters["retire_date"].replace("'", "\\'")

	return conditions
