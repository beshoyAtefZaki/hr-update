# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.model.document import Document

class HRSettings(Document):
	def validate(self):
		from erpnext.setup.doctype.naming_series.naming_series import set_by_naming_series
		set_by_naming_series("Employee", "employee_number",
			self.get("emp_created_by")=="Naming Series", hide_name_field=True)
		if self.min_years_of_service < 0:
			frappe.throw(_("Min Years Of Service can't be less than Zero"))
		elif self.days_of_first_five_years <= 0:
			frappe.throw(_("Days Of First Five Years can't be less than Zero "))
		elif self.days_after_five_years <= 0:
			frappe.throw(_("Days After Five Years can't be less than Zero "))
		elif self.p1 < 0:
			frappe.throw(_("P1 can't be less than Zero "))
		elif self.p2 < 0:
			frappe.throw(_("P2 can't be less than Zero "))
		elif self.p3 < 0:
			frappe.throw(_("P3 can't be less than Zero "))
		elif self.retirement_age_for_male < 0:
			frappe.throw(_("Retirement Age For Male can't be less than Zero "))
		elif self.retirement_age_for_female < 0:
			frappe.throw(_("Retirement Age For Female can't be less than Zero "))
		elif self.min_age_for_emp < 0:
			frappe.throw(_("Min Age For Emp can't be less than Zero "))