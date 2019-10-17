# -*- coding: utf-8 -*-
# Copyright (c) 2017, Ebkar Technology & Management Solutions and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe import _,throw
from frappe.utils import get_datetime
from frappe.model.document import Document

class InterviewEvaluation(Document):
	def validate(self):

		if (get_datetime(self.interview_end_time) < get_datetime(self.interview_start_time)):
			throw(_("Interview End Time must be greater than Interview Start Time"))
