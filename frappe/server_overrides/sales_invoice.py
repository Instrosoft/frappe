import frappe
from frappe.utils.data import add_years
from datetime import datetime, timedelta
from frappe.data_api.data import send_invoice

def on_submit(doc,method=None):
    if not doc.custom_quotation_number:
        return 
    frappe.db.set_value("Quotation", doc.custom_quotation_number, "status", "Ordered")

def on_cancel(doc,method=None):
    if not doc.custom_quotation_number:
        return 
    frappe.db.set_value("Quotation", doc.custom_quotation_number, "status", "Open")

def before_insert(doc,method=None):
    start_date = frappe.db.get_value("Company",doc.company,"creation")
    end_date = add_years(start_date,1)
    doc.custom_end_date = end_date

def before_cancel(doc,method=None):
    try:
        posting_date = datetime.strptime(doc["posting_date"], "%Y-%m-%d").date() #convert string to date object
        current_date = datetime.now().date()
    except ValueError:
        return False

    day_difference = (current_date - posting_date).days

    if day_difference > 3 or day_difference < 0:
        frappe.throw("This invoice was posted over 3 days ago and cannot be canceled as per company policy.")

def on_update(doc,method=None):
    if not doc.has_value_changed("workflow_state"):
        return
    
    if not frappe.db.get_value("Company",doc.company,"custom_enable_einvoicing"):
        return

    if doc.workflow_state == "Pending":
        if doc.custom_validation_failure_reason == "failed" or doc.custom_validation_failure_reason:
            doc.db_set({"custom_api_status": "", "custom_validation_failure_reason": ""})
        send_invoice(doc.as_json())
        frappe.msgprint("Invoice Sent for Validation. Please check after some time. Refresh the page to see the updated status.")