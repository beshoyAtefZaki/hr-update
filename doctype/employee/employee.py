
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from dateutil.relativedelta import relativedelta

from frappe.utils import getdate, validate_email_add, today, add_years, add_days, cstr
from frappe.model.naming import make_autoname
from frappe import throw, _, scrub
import frappe.permissions
from datetime import datetime
from frappe.model.document import Document
from erpnext.utilities.transaction_base import delete_events
from frappe.utils.nestedset import NestedSet
from frappe.utils.background_jobs import enqueue


class EmployeeUserDisabledError(frappe.ValidationError):
    pass


class OverlapError(frappe.ValidationError): pass


class Employee(NestedSet):
    nsm_parent_field = 'reports_to'

    def autoname(self):
        naming_method = frappe.db.get_value("HR Settings", None, "emp_created_by")
        if not naming_method:
            throw(_("Please setup Employee Naming System in Human Resource > HR Settings"))
        else:
            if naming_method == 'Naming Series':
                self.name = make_autoname(self.naming_series + '.####')
            elif naming_method == 'Employee Number':
                self.name = self.employee_number
            elif naming_method == 'Full Name':
                self.name = self.employee_name

        self.employee = self.name

    def validate(self):
        from erpnext.controllers.status_updater import validate_status
        validate_status(self.status, ["Active", "Left"])

        self.employee = self.name
        self.validate_date()
        self.validate_email()
        self.validate_position()
        self.validate_status()
        self.validate_employee_leave_approver()
        self.validate_reports_to()
        self.validate_prefered_email()
        self.validate_stop_working_date()
        self.validate_medical_data()
        #self.validate_resident_data()
        self.validate_attendance_data()

        if self.user_id:
            self.validate_user_details()
        else:
            existing_user_id = frappe.db.get_value("Employee", self.name, "user_id")
            if existing_user_id:
                frappe.permissions.remove_user_permission(
                    "Employee", self.name, existing_user_id)

        if self.finger_print_number:
            self.validate_duplicate_finger_print_number()


        #customization empolyee model
        #create salary strucrture for new employee

        # self.create_salary_Structure (self.company ,
        #                               self.salary_details , self.name ,
        #                               self.employee_name ,self.date_of_joining )

    # create_salary_Structure
    def create_salary_Structure(self ,company ,salary_detail ,name ,employee_name ,date_of_joining):
            #if user add slaray detail to the employee

            # checkIfOld = frappe.db.get_value("Salary Structure" ,name ,['is_active'],as_dict=1)
            #
            # if  checkIfOld == None :

            if salary_detail :
                salary_Structure             = frappe.new_doc("Salary Structure")
                salary_Structure.name   = name
                salary_Structure.company     = company
                salary_Structure.letter_head = "Al-RASSEN"
                salary_Structure.is_active   = "Yes"
                employees =salary_Structure.append('employees' ,{})
                employees.employee  =  name
                employees.employee_name =  employee_name
                employees.from_date =    date_of_joining
                for i in salary_detail :
                    if i.salary_component == "Basic":
                        employees.base = i.amount

                # deductions = salary_Structure.append('deductions' ,{})
                        for i in salary_detail :
                            component_type = frappe.db.get_value("Salary Component" ,i.salary_component ,['type'],as_dict=1)
                            if component_type.type == "Earning"  :
                                earnings  =  salary_Structure.append('earnings' ,{})
                                earnings.salary_component =  i.salary_component
                                earnings.amount_based_on_formula = False
                                earnings.amount = i.amount
                                earnings.depends_on_lwp = True
                salary_Structure.mode_of_payment = u"صندوق النقدية العام"
                salary_Structure.payment_account=u"120102 - صندوق النقدية العام - RS"
                salary_Structure.save()



    def validate_user_details(self):
        data = frappe.db.get_value('User',
                                   self.user_id, ['enabled', 'user_image'], as_dict=1)
        if data.get("user_image"):
            self.image = data.get("user_image")
        self.validate_for_enabled_user_id(data.get("enabled", 0))
        self.validate_duplicate_user_id()

    def validate_stop_working_date(self):
        stop_working_dict = self.get("stop_working_data")
        for item in stop_working_dict:
            tem_pdate = add_days(datetime.strptime(item.start_date, '%Y-%m-%d'), 180)
            if (datetime.strptime(item.start_date, '%Y-%m-%d') > datetime.strptime(item.end_date, '%Y-%m-%d')):
                frappe.throw(_("Start Date should not exceed End Date"), title=_("STOP WORKING DATA"))
            elif (datetime.strptime(item.end_date, '%Y-%m-%d') > tem_pdate):
                frappe.throw(_("End Date should not exceed than 180 day"), title=_("STOP WORKING DATA"))
            elif (item.cut_percentage != ""):
                if (float(item.cut_percentage) > 50):
                    frappe.throw(_("Cut percentage should not exceed than 50%"), title=_("STOP WORKING DATA"))

            existing = self.check_stop_working_dates(item)
            if existing:
                frappe.throw(_("You have overlap in Row {0}: Start From and End Date of {1} ")
                             .format(item.idx, self.name), OverlapError, title=_("STOP WORKING DATA"))

    def validate_medical_data(self):
        employee_medical_documents = self.get("employee_medical_documents")
        for item in employee_medical_documents:
            if item.start_date and item.end_date:
                if (datetime.strptime(item.start_date, '%Y-%m-%d') > datetime.strptime(item.end_date, '%Y-%m-%d')):
                    frappe.throw(_("Start Date  should not exceed End Date"), title=_("MEDICAL DOCUMENTS"))
            existing = self.check_medical_data_dates(item)
            if existing:
                frappe.throw(_("You have overlap in Row {0}: Start Date and End Date of {1} ")
                             .format(item.idx, self.name), OverlapError, title=_("MEDICAL DOCUMENTS"))

    def check_medical_data_dates(self, item):
        # check internal overlap
        for employee_medical_document in self.employee_medical_documents:
            # end_date = employee_medical_document.end_date
            if not employee_medical_document.end_date:
                if item.idx != employee_medical_document.idx and (employee_medical_document.start_date < item.end_date):
                    return self

            if (item.idx != employee_medical_document.idx) and employee_medical_document.end_date and (
                    (
                            item.start_date > employee_medical_document.start_date and item.start_date < employee_medical_document.end_date) or
                    (
                            item.end_date > employee_medical_document.start_date and item.end_date < employee_medical_document.end_date) or
                    (
                            item.start_date <= employee_medical_document.start_date and item.end_date >= employee_medical_document.end_date)):
                return self

    def check_stop_working_dates(self, item):
        # check internal overlap
        for stop_working in self.stop_working_data:

            if item.idx != stop_working.idx and (
                    (
                            item.start_date > stop_working.start_date and item.start_date < stop_working.end_date) or
                    (
                            item.end_date > stop_working.start_date and item.end_date < stop_working.end_date) or
                    (
                            item.start_date <= stop_working.start_date and item.end_date >= stop_working.end_date)):
                return self

    def validate_resident_data(self):
        employee_resident_data = self.get("employee_resident_data")
        for item in employee_resident_data:
            if (datetime.strptime(item.release_start_date, '%Y-%m-%d') > datetime.strptime(item.release_end_date,
                                                                                           '%Y-%m-%d')):
                frappe.throw(_("Release Start Date should not exceed Release End Date"), title=_("RESIDENT DATA"))

            existing = self.check_resident_dates(item)
            if existing:
                frappe.throw(_("You have overlap in Row {0}: Release Start Date and Release End Date of {1} ")
                             .format(item.idx, self.name), OverlapError, title=_("RESIDENT DATA"))

    def validate_attendance_data(self):
        employee_attendance_data = self.get("employee_attendance_data")
        for item in employee_attendance_data:
            # period_start_date = frappe.db.get_value("Attendance Period", {"period_name": item.attendance_period},
            #                                         "start_date")
            # period_end_date = frappe.db.get_value("Attendance Period", {"period_name": item.attendance_period},
            #                                       "end_date")
            period_start_date = "12-9-2018"
            period_end_date   = "12-9-2018"
            if (datetime.strptime(item.start_date, '%Y-%m-%d') < datetime.strptime(cstr(period_start_date),
                                                                                   '%Y-%m-%d')):
                frappe.throw(_("Start Date should not be before Period Start Date"), title=_("ATTENDANCE DATA"))

            if item.end_date:
                if (datetime.strptime(item.end_date, '%Y-%m-%d') > datetime.strptime(cstr(period_end_date),
                                                                                     '%Y-%m-%d')):
                    frappe.throw(_("End Date should not exceed Period End Date"), title=_("ATTENDANCE DATA"))

                if (datetime.strptime(item.start_date, '%Y-%m-%d') > datetime.strptime(item.end_date, '%Y-%m-%d')):
                    frappe.throw(_("Start Date should not exceed End Date"), title=_("ATTENDANCE DATA"))

            existing = self.check_attendance_dates(item)
            if existing:
                frappe.throw(_("You have overlap in Row {0}: Start Date and  End Date of {1} ")
                             .format(item.idx, self.name), OverlapError, title=_("ATTENDANCE DATA"))

    def check_attendance_dates(self, item):
        # check internal overlap
        for attendance_data in self.employee_attendance_data:
            # end_date = attendance_data.end_date
            if not attendance_data.end_date:
                if item.idx != attendance_data.idx and (attendance_data.start_date < item.end_date):
                    return self

            if (item.idx != attendance_data.idx) and attendance_data.end_date and (
                    (
                            item.start_date > attendance_data.start_date and item.start_date < attendance_data.end_date) or
                    (
                            item.end_date > attendance_data.start_date and item.end_date < attendance_data.end_date) or
                    (
                            item.start_date <= attendance_data.start_date and item.end_date >= attendance_data.end_date)):
                return self

    def check_resident_dates(self, item):
        # check internal overlap
        for resident_data in self.employee_resident_data:
            if item.idx != resident_data.idx and (
                    (
                            item.release_start_date > resident_data.release_start_date and item.release_start_date < resident_data.release_end_date) or
                    (
                            item.release_end_date > resident_data.release_start_date and item.release_end_date < resident_data.release_end_date) or
                    (
                            item.release_start_date <= resident_data.release_start_date and item.release_end_date >= resident_data.release_end_date)):
                return self

    def update_nsm_model(self):
        frappe.utils.nestedset.update_nsm(self)

    def on_update(self):
        self.update_nsm_model()
        if self.user_id:
            self.update_user()
            self.update_user_permissions()

    def update_user_permissions(self):
        frappe.permissions.add_user_permission("Employee", self.name, self.user_id)
        frappe.permissions.set_user_permission_if_allowed("Company", self.company, self.user_id)

    def update_user(self):
        # add employee role if missing
        user = frappe.get_doc("User", self.user_id)
        user.flags.ignore_permissions = True

        if "Employee" not in user.get("roles"):
            user.add_roles("Employee")

        # copy details like Fullname, DOB and Image to User
        if self.employee_name and not (user.first_name and user.last_name):
            employee_name = self.employee_name.split(" ")
            if len(employee_name) >= 3:
                user.last_name = " ".join(employee_name[2:])
                user.middle_name = employee_name[1]
            elif len(employee_name) == 2:
                user.last_name = employee_name[1]

            user.first_name = employee_name[0]

        if self.date_of_birth:
            user.birth_date = self.date_of_birth

        if self.gender:
            user.gender = self.gender

        if self.image:
            if not user.user_image:
                user.user_image = self.image
                try:
                    frappe.get_doc({
                        "doctype": "File",
                        "file_name": self.image,
                        "attached_to_doctype": "User",
                        "attached_to_name": self.user_id
                    }).insert()
                except frappe.DuplicateEntryError:
                    # already exists
                    pass

        user.save()

    def validate_date(self):
        if self.date_of_birth and getdate(self.date_of_birth) > getdate(today()):
            throw(_("Date of Birth cannot be greater than today."))

        min_age_for_emp = int(frappe.db.get_single_value("HR Settings", "min_age_for_emp") or 16)
        if relativedelta(getdate(today()), getdate(self.date_of_birth)).years < min_age_for_emp:
            throw(_("Employee Age should be greater than {0}").format(min_age_for_emp))

        if self.date_of_birth and self.date_of_joining and getdate(self.date_of_birth) >= getdate(self.date_of_joining):
            throw(_("Date of Joining must be greater than Date of Birth"))

        elif self.date_of_retirement and self.date_of_joining and (
                getdate(self.date_of_retirement) <= getdate(self.date_of_joining)):
            throw(_("Date Of Retirement must be greater than Date of Joining"))

        elif self.relieving_date and self.date_of_joining and (
                getdate(self.relieving_date) <= getdate(self.date_of_joining)):
            throw(_("Relieving Date must be greater than Date of Joining"))

        elif self.contract_end_date and self.date_of_joining and (
                getdate(self.contract_end_date) <= getdate(self.date_of_joining)):
            throw(_("Contract End Date must be greater than Date of Joining"))

        elif self.reason_for_resignation in ["Married", "Have Baby"] and not self.marital_status_date:
            throw(_("Please enter Marital Status Date"))

    def validate_email(self):
        if self.company_email:
            validate_email_add(self.company_email, True)
        if self.personal_email:
            validate_email_add(self.personal_email, True)

    def validate_position(self):
        position = None
        unused_positions = get_unused_position('Positions', '', 'name', 0, False,
                            [['designation','=', self.designation], ['department', '=', self.department]])

        result_pos = frappe.db.sql_list("""select position from `tabEmployee` where
                   position=%s and status='Active' """, (self.position))
        if result_pos:
            position = result_pos[0]

        if position == self.position:
            pass
        else:
            if ((self.position,) not in unused_positions):
                frappe.throw(_("Position {0} not in available Positions ").format(self.position))


    def validate_status(self):
        if self.status == 'Left' and not self.relieving_date:
            throw(_("Please enter relieving date."))
        if self.status == 'Left' and self.relieving_date and self.employment_type == "Intern":
            days_after_contract_end = relativedelta(getdate(self.relieving_date), getdate(self.contract_end_date)).days
            days_of_intern = relativedelta(getdate(self.contract_end_date), getdate(self.date_of_joining)).days
            if days_after_contract_end < days_of_intern:
                frappe.msgprint(_(
                    "You have assigned {0} days of Intern Employee have only spent {1} days after Contract End").format(
                    days_of_intern, days_after_contract_end))

    def validate_for_enabled_user_id(self, enabled):
        if not self.status == 'Active':
            return

        if enabled is None:
            frappe.throw(_("User {0} does not exist").format(self.user_id))
        if enabled == 0:
            frappe.throw(_("User {0} is disabled").format(self.user_id), EmployeeUserDisabledError)

    def validate_duplicate_user_id(self):
        employee = frappe.db.sql_list("""select name from `tabEmployee` where
			user_id=%s and status='Active' and name!=%s""", (self.user_id, self.name))
        if employee:
            throw(_("User {0} is already assigned to Employee {1}").format(
                self.user_id, employee[0]), frappe.DuplicateEntryError)

    def validate_duplicate_finger_print_number(self):
        employee = frappe.db.sql_list("""select name from `tabEmployee` where
            finger_print_number=%s and status='Active' and name!=%s""", (self.finger_print_number, self.name))
        if employee:
            throw(_("Finger Print Number {0} is already assigned to Employee {1}").format(
                self.finger_print_number, employee[0]), frappe.DuplicateEntryError)

    def validate_employee_leave_approver(self):
        for l in self.get("leave_approvers")[:]:
            if "Leave Approver" not in frappe.get_roles(l.leave_approver):
                frappe.get_doc("User", l.leave_approver).add_roles("Leave Approver")

    def validate_reports_to(self):
        if self.reports_to == self.name:
            throw(_("Employee cannot report to himself."))

    def on_trash(self):
        self.update_nsm_model()
        delete_events(self.doctype, self.name)

    def validate_prefered_email(self):
        if self.prefered_contact_email and not self.get(scrub(self.prefered_contact_email)):
            frappe.msgprint(_("Please enter " + self.prefered_contact_email))




def get_timeline_data(doctype, name):
    '''Return timeline for attendance'''
    return dict(frappe.db.sql('''select unix_timestamp(attendance_date), count(*)
		from `tabAttendance` where employee=%s
			and attendance_date > date_sub(curdate(), interval 1 year)
			and status in ('Present', 'Half Day')
			group by attendance_date''', name))


@frappe.whitelist()
def get_retirement_date(date_of_birth=None):
    ret = {}
    if date_of_birth:
        try:
            retirement_age = int(frappe.db.get_single_value("HR Settings", "retirement_age") or 60)
            dt = add_years(getdate(date_of_birth), retirement_age)
            ret = {'date_of_retirement': dt.strftime('%Y-%m-%d')}
        except ValueError:
            # invalid date
            ret = {}

    return ret


def validate_employee_role(doc, method):
    # called via User hook
    if "Employee" in [d.role for d in doc.get("roles")]:
        if not frappe.db.get_value("Employee", {"user_id": doc.name}):
            frappe.msgprint(_("Please set User ID field in an Employee record to set Employee Role"))
            doc.get("roles").remove(doc.get("roles", {"role": "Employee"})[0])


def update_user_permissions(doc, method):
    # called via User hook
    if "Employee" in [d.role for d in doc.get("roles")]:
        employee = frappe.get_doc("Employee", {"user_id": doc.name})
        employee.update_user_permissions()


def send_birthday_reminders():
    """Send Employee birthday reminders if no 'Stop Birthday Reminders' is not set."""
    if int(frappe.db.get_single_value("HR Settings", "stop_birthday_reminders") or 0):
        return

    from frappe.utils.user import get_enabled_system_users
    users = None

    birthdays = get_employees_who_are_born_today()

    if birthdays:
        if not users:
            users = [u.email_id or u.name for u in get_enabled_system_users()]

        for e in birthdays:
            frappe.sendmail(recipients=filter(lambda u: u not in (e.company_email, e.personal_email, e.user_id), users),
                            subject=_("Birthday Reminder for {0}").format(e.employee_name),
                            message=_("""Today is {0}'s birthday!""").format(e.employee_name),
                            reply_to=e.company_email or e.personal_email or e.user_id)


def send_resident_data_reminder():
    if int(frappe.db.get_single_value("HR Settings", "stop_resident_data_reminders") or 0):
        return

    resident_data_reminder = int(frappe.db.get_single_value("HR Settings", "resident_data_reminder") or 0)
    resident_employees = get_employees_resident_data(resident_data_reminder)
    if resident_employees:
        hr_users = get_HR_Users()
        email_args = {
            "recipients": hr_users,
            "message": _("""Please check RESIDENT DATA for these EMP {0}""").format(str(resident_employees)),
            "subject": _("Resident Employees License"),
            "now": True,

        }
        enqueue(method=frappe.sendmail, queue='short',
                timeout=300, async=True, **email_args)


# return frappe.msgprint(_("{0} Release End Date is soon").format(emp))
# frappe.throw(_('Reference') + ': <a href="#Form/Leave Allocation/{0}">{0}</a>'
#              .format(leave_allocation[0][0]), OverlapError)

def get_HR_Users():
    return frappe.db.sql_list("""
    		SELECT parent FROM `tabHas Role` WHERE `role` ='HR User' and `parenttype` = 'user' and parent <> 'Administrator'
    		""")


def get_employees_resident_data(resident_data_reminder):
    return frappe.db.sql_list("""select parent
		from `tabResident Data` where DATEDIFF(release_end_date,CURDATE() ) <= (%(day)s) and DATEDIFF(release_end_date,CURDATE() ) >= 0
		""", {"day": resident_data_reminder})


def get_employees_who_are_born_today():
    """Get Employee properties whose birthday is today."""
    return frappe.db.sql("""select name, personal_email, company_email, user_id, employee_name
		from tabEmployee where day(date_of_birth) = day(%(date)s)
		and month(date_of_birth) = month(%(date)s)
		and status = 'Active'""", {"date": today()}, as_dict=True)


def get_holiday_list_for_employee(employee, raise_exception=True):
    if employee:
        holiday_list, company = frappe.db.get_value("Employee", employee, ["holiday_list", "company"])
    else:
        holiday_list = ''
        company = frappe.db.get_value("Global Defaults", None, "default_company")

    if not holiday_list:
        holiday_list = frappe.db.get_value("Company", company, "default_holiday_list")

    if not holiday_list and raise_exception:
        frappe.throw(_('Please set a default Holiday List for Employee {0} or Company {1}').format(employee, company))

    return holiday_list


def is_holiday(employee, date=None):
    '''Returns True if given Employee has an holiday on the given date
    :param employee: Employee `name`
    :param date: Date to check. Will check for today if None'''

    holiday_list = get_holiday_list_for_employee(employee)
    if not date:
        date = today()

    if holiday_list:
        return frappe.get_all('Holiday List', dict(name=holiday_list, holiday_date=date)) and True or False


@frappe.whitelist()
def deactivate_sales_person(status=None, employee=None):
    if status == "Left":
        sales_person = frappe.db.get_value("Sales Person", {"Employee": employee})
        if sales_person:
            frappe.db.set_value("Sales Person", sales_person, "enabled", 0)


@frappe.whitelist()
def create_user(employee, user=None, email=None):
    emp = frappe.get_doc("Employee", employee)

    employee_name = emp.employee_name.split(" ")
    middle_name = last_name = ""

    if len(employee_name) >= 3:
        last_name = " ".join(employee_name[2:])
        middle_name = employee_name[1]
    elif len(employee_name) == 2:
        last_name = employee_name[1]

    first_name = employee_name[0]

    if email:
        emp.prefered_email = email

    user = frappe.new_doc("User")
    user.update({
        "name": emp.employee_name,
        "email": emp.prefered_email,
        "enabled": 1,
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "gender": emp.gender,
        "birth_date": emp.date_of_birth,
        "phone": emp.cell_number,
        "bio": emp.bio
    })
    user.insert()
    return user.name

@frappe.whitelist()
def create_position(designation, department):

    position = frappe.new_doc("Positions")
    position.update({
        "designation": designation,
        "department":  department
    })
    position.insert()
    return position.name

def get_employee_emails(employee_list):
    '''Returns list of employee emails either based on user_id or company_email'''
    employee_emails = []
    for employee in employee_list:
        if not employee:
            continue
        user, email = frappe.db.get_value('Employee', employee, ['user_id', 'company_email'])
        if user or email:
            employee_emails.append(user or email)

    return employee_emails


@frappe.whitelist()
def get_unused_position(doctype, txt, searchfield, start, page_len, filters):
    from frappe.desk.reportview import get_match_cond, get_filters_cond
    conditions = []

    if not page_len:
        return frappe.db.sql("""
                select `name`
                    from tabPositions
                    where `status`='Active'
                    and name not in (select position  from tabEmployee where position is not NULL)
                    and ({key} like %(txt)s)
                    {fcond} {mcond}
                order by
                    if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999) desc """.format(**{
            'key': searchfield,
            'fcond': get_filters_cond(doctype, filters, conditions),
            'mcond': get_match_cond(doctype)
        }), {
                                 'txt': "%%%s%%" % txt,
                                 '_txt': txt.replace("%", ""),
                             })
    else:
        return frappe.db.sql("""
                select `name`
                    from tabPositions
                    where `status`='Active'
                    and name not in (select position  from tabEmployee where position is not NULL)
                    and ({key} like %(txt)s)
                    {fcond} {mcond}
                order by
                    if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999) desc

                limit %(start)s, %(page_len)s""".format(**{
            'key': searchfield,
            'fcond': get_filters_cond(doctype, filters, conditions),
            'mcond': get_match_cond(doctype)
        }), {
                                 'txt': "%%%s%%" % txt,
                                 '_txt': txt.replace("%", ""),
                                 'start': start,
                                 'page_len': page_len
                             })


@frappe.whitelist()
def get_children(doctype, parent=None, company=None, is_root=False, is_tree=False):
    condition = ''

    if is_root:
        parent = ""
    if parent and company and parent != company:
        condition = ' and reports_to = "{0}"'.format(frappe.db.escape(parent))
    else:
        condition = ' and ifnull(reports_to, "")=""'

    employee = frappe.db.sql("""
		select
			name as value, employee_name as title,
			exists(select name from `tabEmployee` where reports_to=emp.name) as expandable
		from
			`tabEmployee` emp
		where company='{company}' {condition} order by name"""
                             .format(company=company, condition=condition), as_dict=1)

    return employee


@frappe.whitelist()
def get_retirement_date_for_gender(date_of_birth=None, gender=None):
    ret = {}
    if date_of_birth and gender:
        try:
            if gender == 'Male':
                retirement_age = int(frappe.db.get_single_value("HR Settings", "retirement_age_for_male") or 60)
            elif gender == 'Female':
                retirement_age = int(frappe.db.get_single_value("HR Settings", "retirement_age_for_female") or 55)
            dt = add_years(getdate(date_of_birth), retirement_age)
            ret = {'date_of_retirement': dt.strftime('%Y-%m-%d')}
        except ValueError:
            # invalid date
            ret = {}

    return ret


@frappe.whitelist()
def get_test_period_end_date(date_of_joining=None):
    ret = {}
    if date_of_joining:
        try:
            test_days = int(frappe.db.get_single_value("HR Settings", "test_period") or 90)
            dt = add_days(getdate(date_of_joining), test_days)
            ret = {'test_period_end_date': dt.strftime('%Y-%m-%d')}
        except ValueError:
            # invalid date
            ret = {}

    return ret



#auto create salary structure
@frappe.whitelist()
def create_salary_Structure(company  ,name ,employee_name ,date_of_joining):
        #if user add slaray detail to the employee

        checkIfOld = frappe.db.get_value("Salary Structure" ,name ,['is_active'],as_dict=1)
        #
        # salary_detail  =frappe.get_doc('Salary Detail', name,
        #                                 as_dict=1)
        # salary_detail  =frappe.get_list('Salary Detail',filters={'parent': name} ,fields =['amount' ,'salary_component']
                                        # )
        # employee_salary_detail  =frappe.get_list('Employee', filters={'name': name} )
        # salary_detail  = employee_salary_detail.salary_details
        # salary_detail  = frappe.db.sql(""" SELECT salary_component , amount , """)
        # lis = []
        salary_detail  = frappe.get_doc("Employee" ,  name)
        # salary_detail  = frappe.db.sql(""" SELECT * FROM `tabEmployee` WHERE employee  = (%s) """%name , as_dict=1)
        frappe.throw(_(salary_detail))
        # salary_Structure  = frappe.new_doc("Salary Structure")
        # if  checkIfOld == None :
        #     # frappe.throw(_(checkIfOld))
        #     #create new salary structure
        #     salary_Structure  = frappe.new_doc("Salary Structure")
        if  checkIfOld == None :
            salary_Structure  = frappe.new_doc("Salary Structure")
        if  checkIfOld != None :
            #update existing salary structure
            salary_Structure  =frappe.get_doc('Salary Structure', name)
            salary_Structure.set('earnings' ,{})
            salary_Structure.set('employees' ,{})
            # salary_Structure.earnings=[]
            #
            # salary_Structure.save()
            # salary_Structure .delete()
            # salary_Structure  = frappe.new_doc("Salary Structure")
            # frappe.throw(_(salary_Structure.earnings))
            # old_salary_detail =   frappe.get_doc('Salary Detail', old)
            # old_salary_detail.delete()




            # frappe.throw(_("deleted"))
            # for e in salary_Structure.employees :
            #     employee_old = e.name
            # old_employee_table =  frappe.get_doc('Salary Structure Employee', employee_old)
            # old_employee_table.delete()
            # # old_employee_table.save()
            # for i in salary_Structure.earnings :
            #     old = i.name
            # old_salary_detail =   frappe.get_doc('Salary Detail', old)
            # old_salary_detail.delete()
            # # old_salary_detail.save()


        # salary_Structure.set('earnings' ,[])
        if salary_detail :
            # frappe.throw(_(salary_detail))
            salary_Structure.name   = name
            salary_Structure.company     = company
            salary_Structure.letter_head = "Al-RASSEN"
            salary_Structure.is_active   = "Yes"
            employees =salary_Structure.append('employees' ,{})
            employees.employee  =  name
            employees.employee_name =  employee_name
            employees.from_date =    date_of_joining


            for i in salary_detail :
                if i.salary_component == "Basic":
                    employees.base = i.amount
                    # deductions = salary_Structure.append('deductions' ,{})
            for i in salary_detail :
                component_type = frappe.db.get_value("Salary Component" ,i.salary_component ,['type'],as_dict=1)
                if component_type.type == "Earning"  :
                    earnings  =  salary_Structure.append('earnings' ,{})
                    earnings.salary_component =  i.salary_component
                    earnings.amount_based_on_formula = False
                    earnings.amount = i.amount
                    earnings.depends_on_lwp = True
            salary_Structure.mode_of_payment = u"صندوق النقدية العام"
            salary_Structure.payment_account=u"120102 - صندوق النقدية العام - RS"
            salary_Structure.save()
