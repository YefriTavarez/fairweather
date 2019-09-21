import frappe

from frappe.desk.reportview import get_match_cond, get_filters_cond

def customer_with_credit_query(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql("""select name, customer_name, customer_group from `tabCustomer`
		where docstatus < 2
			and disabled = 0
			and ({key} like %(txt)s
				or customer_name like %(txt)s
				or customer_group like %(txt)s)
			{mcond}
		order by
			if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
			if(locate(%(_txt)s, customer_name), locate(%(_txt)s, customer_name), 99999),
			if(locate(%(_txt)s, customer_group), locate(%(_txt)s, customer_group), 99999),
			name, customer_name
		limit %(start)s, %(page_len)s""".format(**{
			'key': searchfield,
			'mcond':get_match_cond(doctype)
		}), {
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})
