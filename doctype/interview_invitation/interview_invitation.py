# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _,throw
from frappe.utils import get_datetime
from frappe.model.document import Document
from erpnext.hr.doctype.employee.employee import get_employee_emails

class InterviewInvitation(Document):
	def onload(self):
		interview_evaluation = frappe.get_all("Interview Evaluation", filters={"applicant_name": self.job_applicant})
		if interview_evaluation:
			self.get("__onload").interview_evaluation = interview_evaluation[0].name

	def on_submit(self):
		receiver = frappe.db.get_value("Job Applicant", self.job_applicant, "email_id")
		msg = frappe.render_template("templates/emails/interview_invitation.html", {
			"doc": self
		})

		frappe.sendmail(recipients= [receiver],
						cc=get_employee_emails([d.interviewer_name for d in self.interviewers]),
						message=msg,
						subject=_("Interview with {0} for {1} position").format(self.applicant_name,self.job_title))

	def validate(self):

		if (get_datetime(self.end_date) < get_datetime(self.start_date)):
			throw(_("End Date must be greater than Start Date"))


@frappe.whitelist()
def get_interviewers(doctype, txt, searchfield, start, page_len, filters):
	from frappe.desk.reportview import get_match_cond, get_filters_cond

	conditions = []
	return frappe.db.sql("""SELECT emp.name,emp.employee_name
 				FROM `tabHas Role` as role
				INNER JOIN `tabEmployee` as emp 
				WHERE role.parent = emp.user_id 
 				and role.role ='Interviewer' and role.`parenttype` = 'user' and role.parent <> 'Administrator'
				and role.docstatus < 2
				and ({key} like %(txt)s)
                {fcond} {mcond}
			 order by
                if(locate(%(_txt)s, role.parent), locate(%(_txt)s, role.parent), 99999) desc

			limit %(start)s, %(page_len)s""".format(**{
				'key': 'emp.employee_name',
				'fcond': get_filters_cond(doctype, filters, conditions),
				'mcond': get_match_cond(doctype)
				}), {
				 'txt': "%%%s%%" % txt,
				 '_txt': txt.replace("%", ""),
				 'start': start,
				 'page_len': page_len
			})
