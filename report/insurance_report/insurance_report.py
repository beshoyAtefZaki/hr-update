# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from time import strptime
from frappe import _

def execute(filters=None):
	if not filters:
			filters = {}

	columns, data = [], []

	columns = get_columns()
	data = get_positions(filters)

	return columns, data


def get_columns():
	return [
            _("Department") + ":Link/Department:120",
            _("employee") + ":Link/Employee:120",
            _("Employee Insurance Share") +":Currency/Employee Insurance Share:120",
           	_("Company Insurance Share") +
         	  ":Currency/Company Insurance Share:120",
           	_("E-Medical insurance Share") +
         	  ":Currency/E-Medical insurance Share:120",
           	_("Co-Medical insurance Share") +
         	  ":Currency/Co-Medical insurance Share:120"
        ]


def get_positions(filters):
	conditions = get_conditions(filters)
	return frappe.db.sql("""
		select 	department, employee ,
			SUM(case when salary_component='Employee Insurance Share' then amount else 0 end )  'Employee Insurance Share',
			SUM(case when salary_component='Company Insurance Share' then amount else 0 end )  'Company Insurance Share',
			SUM(case when salary_component='E-Medical insurance Share' then amount else 0 end )  'E-Medical insurance Share',
			SUM(case when salary_component='Co-Medical insurance Share' then amount else 0 end )  'Co-Medical insurance Share'
			from 
			(
				select SS.department ,SS.employee, SD.salary_component, SD.amount
					from `tabSalary Slip` SS
								inner join
									`tabSalary Detail` SD
								on SS.`name` = SD.parent
						where SD.parentfield ='insurance'
						%s
			)T
			
		GROUP BY employee

	""" % conditions, as_list=1
	)


def get_conditions(filters):
	import datetime
	now = datetime.datetime.now()
	MonthNO = strptime(filters["start_date"].replace("'", "\\'"), '%b').tm_mon
	Current_year = now.year
	filters["start_date"] = str(Current_year)+"-"+str(MonthNO)+"-01"
	conditions = ""
	if filters.get("start_date"):
		conditions += " and SS.start_date = '%s'" % \
                    filters["start_date"].replace("'", "\\'")

	return conditions
