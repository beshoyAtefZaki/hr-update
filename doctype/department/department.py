# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe

from frappe.utils.nestedset import NestedSet,get_root_of
from erpnext.utilities.transaction_base import delete_events

class Department(NestedSet):
	nsm_parent_field = 'parent_department'

	def autoname(self):
		root = get_root_of("Department")
		if root and self.department_name != root and self.department_code:
			self.name = get_abbreviated_name(self.department_name, self.department_code)
		else:
			self.name = self.department_name

	def validate(self):
		if not self.parent_department:
			root = get_root_of("Department")
			if root:
				self.parent_department = root

	def on_update(self):
		NestedSet.on_update(self)

	def on_trash(self):
		super(Department, self).on_trash()
		delete_events(self.doctype, self.name)

def on_doctype_update():
	frappe.db.add_index("Department", ["lft", "rgt"])

def get_abbreviated_name(name, department_code):
	new_name = '{0} - {1}'.format(name, department_code)
	return new_name

@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False):
	condition = "parent_department = '{0}'".format(parent)
	return frappe.db.sql("""
		select
			name as value,
			is_group as expandable
		from `tab{doctype}`
		where
			{condition}
		order by name""".format(doctype=doctype, condition=condition), as_dict=1)

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	args = make_tree_args(**args)
	frappe.get_doc(args).insert()