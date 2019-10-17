# -*- coding: utf-8 -*-
# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _

def execute(filters=None):
	columns,data = get_columns(filters),get_data(filters)
	return columns, data


def get_columns(filters):
	columns =[
		{
			"label": _("Item"),
			"fieldname": "item",
			"width": 120
		},
		{
			"label":_("Male"),
			"fieldname": "male",
			"width": 120
		},
		{
			"label": _("Female"),
			"fieldname": "female",
			"width": 120
		},
		{
			"label": _("Total"),
			"fieldname": "total",
			"width": 120
		},
		{
			"label": _("Percentage"),
			"fieldname": "percentage",
			"width": 120
		},
	]
	return columns

def get_data(filters):
	citizen_male_count,citizen_female_count,total_citizen,total_citizen_per =0,0,0,0
	resident_male_count, resident_female_count, total_resident,total_resident_per = 0, 0, 0,0
	disability_male_count, disability_female_count, total_disability, total_disability_per = 0, 0, 0, 0
	data =[['مواطن', citizen_male_count, citizen_female_count, total_citizen,total_citizen_per],
		   ['مقيم', resident_male_count, resident_female_count, total_resident,total_resident_per],
		   ['صاحب اعاقة', disability_male_count, disability_female_count, total_disability, total_disability_per]]

	employees = frappe.db.sql("""select citizen_or_resident , gender,has_disability from `tabEmployee`
			where status = 'Active'
				and docstatus < 2 """,as_dict=True)
	for emp in employees:
		if emp['citizen_or_resident'] == 'Citizen':
			if emp ['gender'] == 'Male':
				citizen_male_count +=1
			elif emp ['gender'] == 'Female':
				citizen_female_count += 1
		elif emp['citizen_or_resident'] == 'Resident':
			if emp ['gender'] == 'Male':
				resident_male_count +=1
			elif emp ['gender'] == 'Female':
				resident_female_count += 1

		if emp['has_disability']:
			if emp['gender'] == 'Male':
				disability_male_count += 1
			elif emp['gender'] == 'Female':
				disability_female_count += 1

	total_citizen = citizen_male_count +citizen_female_count
	total_resident = resident_male_count +resident_female_count
	total_disability = disability_male_count + disability_female_count

	data[0][1] = citizen_male_count
	data[0][2] = citizen_female_count
	data[0][3] = total_citizen
	data[0][4] = round(float(total_citizen) / len(employees) * 100,2)

	data[1][1] = resident_male_count
	data[1][2] = resident_female_count
	data[1][3] = total_resident
	data[1][4] =round(  float(total_resident) / len(employees)* 100,2)

	data[2][1] = disability_male_count
	data[2][2] = disability_female_count
	data[2][3] = total_disability
	data[2][4] =round(  float(total_disability) / len(employees)* 100,2)

	return data