# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	if not filters:
			filters = {}

	columns = get_columns()
	data = get_positions(filters)

	return columns, data


def get_columns():
	return [
			_("Department") +":Link/Department:120",
			_("Designation") + ":Link/Designation:120",
            _("Position") + ":Data/Position:120",
         	_("Count") + ":Int/Count:120"
			]


def get_positions(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""
			select Department ,designation, position ,COUNT(position) 
				from tabPositions
					where name not in (
					SELECT position from tabEmployee where `status` ='Active' and position is NOT NULL
					)
					%s
					GROUP BY position,department
					
					;

	""" % conditions , as_list=1
	)


def get_conditions(filters):
	# frappe.msgprint(str(filters))
	conditions = ""
	if filters.get("Position"):
		conditions += " and position = '%s'" % \
                    filters["Position"].replace("'", "\\'")

	if filters.get("Designation"):
		conditions += " and designation = '%s'" % \
                    filters["Designation"].replace("'", "\\'")
					
	if filters.get("Department"):
		conditions += " and department = '%s'" % \
                    filters["Department"].replace("'", "\\'")

	if filters.get("Status"):
		conditions += " and `status` = '%s'" % \
                    filters["Status"].replace("'", "\\'")

	return conditions
