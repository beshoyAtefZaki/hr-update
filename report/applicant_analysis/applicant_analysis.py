# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []

	data = get_data(filters)
	data = filter_data(data, filters)

	columns = get_comlumns()

	return columns, data

def get_comlumns():
	columns = [
		_("Applicant Name") + ":Data:200",
		_("Email Address") + ":Data/email_id:120",
		_("Date of Birth") + ":Date:100",
		_("Gender") + ":Link/gender:60",
		_("Job Titles") + ":Link/Job Opening:120",
		_("Skills") + ":Link/Skill:120",
		_("Rating Model") + ":Link/Rating Model:120",
		_("Rate Number") + ":Data:200",
	]

	return columns

def filter_data(data,filters):
	newdata = []

			
	return newdata

def get_data(filters):
	data = []
	condition = get_condition(filters)

	data = frappe.db.sql(
		"""
		select
		TJ.applicant_name ,
		TJ.email_id ,
		TJ.birth_date ,
		TJ.gender ,
		TJ.job_title ,
		TS.skill,
		TS.rating,
           (select `level` from `tabRating Model` where description =TS.rating)
		RateNO
				from  `tabJob Applicant` TJ
			inner join
					tabSkills TS
				on TJ.`name` = TS.parent
				and TJ.`status` ='Open'
				%s
		"""
            % condition , as_list=1,debug=False)

	return data

def get_condition(filters):
	conditions = ""

	if filters.get("Job Opening"):
		conditions += " and TJ.job_title  = '%s'" % \
                    filters["Job Opening"].replace("'", "\\'")

	if filters.get("Skills"):
		skill = frappe.db.get_value(
			"Skills", filters["Skills"].replace("'", "\\'"), "skill")
		conditions += " and TS.skill = '%s'" % skill

	return conditions
