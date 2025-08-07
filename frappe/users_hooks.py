import frappe
from frappe.user_hooks import set_user_permission_for_company
from frappe.permission_hooks import set_user_session_defaults

def handle_user_creation(doc, method):
    """
    Handles multiple actions when a new user is created.
    """
    # Call function to set user permissions for the company
    set_user_permission_for_company(doc, method)

    # Call function to set session defaults for the user
    set_user_session_defaults(doc, method)
