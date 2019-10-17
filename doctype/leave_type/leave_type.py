# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
# from erpnext.utils.utils import validate_Percentage
from frappe.model.document import Document

class LeaveType(Document):

	def validate(self):
		pass
		# validate_Percentage(self.payroll_ratio)
