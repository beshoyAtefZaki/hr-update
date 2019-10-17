# -*- coding: utf-8 -*-
# Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class GetUsers(Document):
	pass




@frappe.whitelist()
def Get_device_Users():
	pass
	# import sys
	#
	# from zk import ZK, const
	#
	# sys.path.append("zk")
	#
	# conn = None
	# zk = ZK('192.168.1.201', port=4370, timeout=5)
	# try:
	# 	print 'Connecting to device ...'
	# 	conn = zk.connect()
	# 	print 'Disabling device ...'
	# 	conn.disable_device()
	# 	print 'Firmware Version: : {}'.format(conn.get_firmware_version())
	# 	# print '--- Get User ---'
	# 	users = conn.get_users()
	# 	# import frappe
	# 	user_Dic = {}# frappe._dict()
	#
	#
	# 	for user in users:
	# 		privilege = 'User'
	# 		if user.privilege == const.USER_ADMIN:
	# 			privilege = 'Admin'
	#
	# 		temp_list = {}
	# 		temp_list["uid"] = user.uid
	# 		temp_list["name"] = user.name
	# 		temp_list["privilege"] = user.privilege
	# 		temp_list["password"] = user.password
	# 		temp_list["group_id"] = user.group_id
	# 		temp_list["user_id"] = user.user_id
	#
	# 		user_Dic[user.user_id] = temp_list
	# 		# print '- UID #{}'.format(user.uid)
	# 		# print '  Name       : {}'.format(user.name)
	# 		# print '  Privilege  : {}'.format(privilege)
	# 		# print '  Password   : {}'.format(user.password)
	# 		# print '  Group ID   : {}'.format(user.group_id)
	# 		# print '  User  ID   : {}'.format(user.user_id)
	#
	# 	# conn.test_voice()
	# 	conn.enable_device()
	# 	print str(user_Dic)
	# except Exception, e:
	# 	print "Process terminate : {}".format(e)
	# finally:
	# 	if conn:
	# 		conn.disconnect()
