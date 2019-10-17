# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

from frappe.website.website_generator import WebsiteGenerator
from frappe import _,throw
from frappe.utils import today
from frappe.utils import getdate

class JobOpening(WebsiteGenerator):
	website = frappe._dict(
		template = "templates/generators/job_opening.html",
		condition_field = "publish",
		page_title_field = "job_title",
	)

	def validate(self):
		if not self.route:
			self.route = frappe.scrub(self.job_title).replace('_', '-')

		if self.publish_date and self.end_date and (getdate(self.end_date) <= getdate(self.publish_date)):
			throw(_("End Date must be greater than Publish Date"))

	def get_context(self, context):
		context.parents = [{'route': 'jobs', 'title': _('All Jobs') }]

def get_list_context(context):
	context.title = _("Jobs")
	context.introduction = _('Current Job Openings')
	context.get_list = get_published_jobs

def get_published_jobs(doctype, txt, filters, limit_start, limit_page_length = 20, order_by='modified desc'):
	published_jobs = frappe.db.sql("""select * from `tabJob Opening`
		where status = 'Open' and publish ='1' and ((%(date)s) BETWEEN publish_date and ifnull(end_date,NOW()))
	    order by publish_date""", {"date": today()}, as_dict = True)
	return published_jobs
