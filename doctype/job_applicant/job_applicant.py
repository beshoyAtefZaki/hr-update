# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.utils import comma_and, validate_email_add
import datetime

sender_field = "email_id"

class DuplicationError(frappe.ValidationError): pass

class JobApplicant(Document):
	def onload(self):
		offer_letter = frappe.get_all("Offer Letter", filters={"job_applicant": self.name})
		interview_invitation = frappe.get_all("Interview Invitation", filters={"job_applicant": self.name})
		if offer_letter:
			self.get("__onload").offer_letter = offer_letter[0].name
		if interview_invitation:
			self.get("__onload").interview_invitation = interview_invitation[0].name

	# def autoname(self): 
	# 	keys = filter(None, (self.applicant_name, self.email_id, self.job_title))
	# 	if not keys:
	# 		frappe.throw(_("Name or Email is mandatory"), frappe.NameError)
	# 	self.name = " - ".join(keys)

	def validate(self):
		self.check_email_id_is_unique()
		if self.email_id:
			validate_email_add(self.email_id, True)

		if not self.applicant_name and self.email_id:
			guess = self.email_id.split('@')[0]
			self.applicant_name = ' '.join([p.capitalize() for p in guess.split('.')])
		try:
			datetime.datetime.strptime(self.birth_date, '%Y-%m-%d')
		except ValueError:
			frappe.throw("Date must be in format: dd-mm-yyyy")

	def check_email_id_is_unique(self):
		if self.email_id:
			names = frappe.db.sql_list("""select name from `tabJob Applicant`
				where email_id=%s and name!=%s and job_title=%s""", (self.email_id, self.name, self.job_title))

			if names:
				frappe.throw(_("Email Address must be unique, already exists for {0}").format(comma_and(names)), frappe.DuplicateEntryError)


# @frappe.whitelist()
