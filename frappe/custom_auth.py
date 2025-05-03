import frappe
from frappe.utils import get_request_site_address

def custom_login_restriction(login_manager):
    user_email = login_manager.user
    current_site = get_request_site_address()
    
    if "admin.invoix.biz" in current_site and user_email != "admin@invoix.biz":
        frappe.throw("Only admin@invoix.biz can log in from this URL.")
