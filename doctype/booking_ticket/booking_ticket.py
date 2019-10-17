# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _,throw
from frappe.model.document import Document
from frappe.utils import getdate, today


class BookingTicket(Document):
	def on_submit(self):
		if self.status == "Open":
			frappe.throw(_("Only Booking Ticket with status 'Approved' and 'Rejected' can be submitted"))

	def validate(self):
		if self.leaving_date <= today():
			throw(_("Leaving Date can't be less than or equal today"))

		if self.leaving_date and self.return_date and (getdate(self.return_date) <= getdate(self.leaving_date)):
			throw(_("Return Date must be greater than Leaving Date"))
