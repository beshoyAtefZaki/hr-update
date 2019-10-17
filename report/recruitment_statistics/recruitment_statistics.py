# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
			filters = {}

	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
			_("Job") +":Link/Job Opening:120",
			_("Job Applicant No") + ":Data/Job Applicant No:120",
			_("Interview Attendance No") + ":Data/Interview Attendance No:120",
			_("Recommended Applicant No") + ":Data/Recommended Applicant No:120",
			]


def get_data(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""
		 SELECT distinct job_title  ,COUNT( `name` ) over (PARTITION by job_title,status) 
		 , sum(if((SELECT `name` from `tabInterview Evaluation` where applicant_name = j.name and docstatus < 2 ) is null,0,1)) over (PARTITION by job_title)
		 , sum(if((SELECT `name` from `tabInterview Evaluation` where applicant_name = j.name and docstatus < 2  and is_recommended_applicant ='Yes') is null,0,1)) over (PARTITION by job_title)
		from `tabJob Applicant`  j
		where `status` <> 'Rejected'
		%s
		order by job_title,status;

	""" % conditions, as_list=1)


def get_conditions(filters):
	conditions = ""
	if filters.get("JobTitle"):
		conditions += " and job_title = '%s'" % filters["JobTitle"].replace("'", "\\'")

	return conditions
