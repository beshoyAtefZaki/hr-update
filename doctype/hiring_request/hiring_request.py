# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class HiringRequest(Document):
	def validate(self):
		# Set readonly fields
		designation_counts = get_designation_counts(self.designation)
		current_count = designation_counts['employee_count']
		current_openings = designation_counts['job_openings']

		if self.number < (current_count + current_openings):
			frappe.throw(_("Number of positions cannot be less then current count of employees"))

@frappe.whitelist()
def get_designation_counts(designation):
	if not designation:
		return False

	employee_counts_dict = {}
	# lft, rgt = frappe.get_cached_value('Company',  company,  ["lft", "rgt"])
	employee_counts_dict["employee_count"] = frappe.db.sql("""select count(*) from `tabEmployee`
		where designation = %s and status='Active'
		""", (designation))[0][0]

	employee_counts_dict['job_openings'] = frappe.db.sql("""select count(*) from `tabJob Opening` \
		where designation=%s and status='Open'
		""", (designation))[0][0]

	return employee_counts_dict
