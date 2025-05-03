import frappe

def set_user_session_defaults(doc, method):
    """
    Automatically set session defaults for the newly created user to their associated company.
    Fetch the company_name directly from the User document.
    """
    # Fetch the company_name directly from the User document
    company_name = doc.company_name  # Replace this with the actual field name in the User doctype

    # Ensure the company_name exists
    if not company_name:
        frappe.throw(f"No company found in the user document for {doc.name}. Please ensure the 'company_name' field is filled.")

    # Set the session default for the new user
    frappe.defaults.set_user_default("Company", company_name, user=doc.name)

    # Confirm action to the admin
    #frappe.msgprint(f"Session default 'Company' has been set to '{company_name}' for the user {doc.name}.")
    default_module_profile = "Accounts and Sales"  # Ensure this Module Profile exists in your system
    doc.module_profile = default_module_profile  # Assign the module profile to the user
    doc.save(ignore_permissions=True)  # Save the user with the updated module profile

    #frappe.msgprint(f"Module Profile '{default_module_profile}' has been assigned to the user {doc.name}.")
