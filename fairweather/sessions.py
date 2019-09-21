import frappe

from frappe import _

from frappe.utils import flt, cint, cstr

no_cache, nocache = (False, False)

def before_login():
	from frappe.auth import delete_session

	allow_users_to_login = frappe.db.get_single_value("System Settings", "allow_users_to_login")
	if not frappe.session.user == "yefritavarez@gmail.com" and not cint(allow_users_to_login): 
		delete_session(frappe.session.sid)
		
		msg = "User {0} has tried to log in at {1}!".format(frappe.session.user, frappe.utils.now_datetime())
		
		frappe.publish_realtime(event='msgprint', message=msg, user='yefritavarez@gmail.com')
		frappe.throw(_("We are updating the system... Please, come back and try within a couple hours!"))