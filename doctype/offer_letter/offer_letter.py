# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class OfferLetter(Document):
	def validate(self):
		self.email = frappe.db.get_value("Job Applicant", self.job_applicant, "email_id")

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.personal_email = frappe.db.get_value("Job Applicant", source.job_applicant, "email_id")
		target.date_of_birth = frappe.db.get_value("Job Applicant", source.job_applicant, "birth_date")
		target.gender = frappe.db.get_value("Job Applicant", source.job_applicant, "gender")
		target.marital_status = frappe.db.get_value("Job Applicant", source.job_applicant, "marital_status")
		target.country = frappe.db.get_value("Job Applicant", source.job_applicant, "country")
		target.cell_number = frappe.db.get_value("Job Applicant", source.job_applicant, "cell_number")
		target.current_accommodation_type = frappe.db.get_value("Job Applicant", source.job_applicant, "current_address_is")
		target.current_address = frappe.db.get_value("Job Applicant", source.job_applicant, "current_address")
		applicant_work_history = frappe.db.get_values("Employee External Work History", {"parenttype": "Job Applicant","parent": source.job_applicant},"*")
		applicant_certifications = frappe.db.get_values("Certifications",{"parenttype": "Job Applicant", "parent": source.job_applicant},"*")
		applicant_education = frappe.db.get_values("Employee Education",{"parenttype": "Job Applicant", "parent": source.job_applicant},"*")
		applicant_skills = frappe.db.get_values("Skills",{"parenttype": "Job Applicant", "parent": source.job_applicant}, "*")

		for applicant_certification in applicant_certifications:
			target.append("certifications", applicant_certification)

		for applicant_skill in applicant_skills:
			target.append("skills", applicant_skill)

		for applicant_work_item in applicant_work_history:
			target.append("external_work_history", applicant_work_item)

		for applicant_education_item in applicant_education:
			target.append("education", applicant_education_item)

	doc = get_mapped_doc("Offer Letter", source_name, {
			"Offer Letter": {
				"doctype": "Employee",
				"field_map": {
					"applicant_name": "employee_name",
				}}
		}, target_doc, set_missing_values)
	return doc
