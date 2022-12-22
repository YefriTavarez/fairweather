import frappe

from frappe import _

from frappe.utils import flt, cint, cstr

no_cache, nocache = (False, False)

def before_login():
	from frappe.auth import delete_session


	allowed_list = (
		"Administrator",
		"yefritavarez@gmail.com",
	)

	if frappe.session.user not in (allowed_list):
		# put this inside the if... one less request to the DB
		system_settings = frappe.get_single("System Settings")
		allow_users_to_login = system_settings.get("allow_users_to_login", default=0)

		if not cint(allow_users_to_login): 
			delete_session(frappe.session.sid)
		
			msg = "User {0} has tried to log in at {1}!".format(frappe.session.user, frappe.utils.now_datetime())
			
			frappe.publish_realtime(event='msgprint', message=msg, user='yefritavarez@gmail.com')
			frappe.throw(_("We are updating the system... Please, come back and try within a couple hours!"))