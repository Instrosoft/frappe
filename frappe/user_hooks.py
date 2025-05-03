import frappe

def set_user_permission_for_company(doc, method):
    """
    Automatically assign a User Permission for the Company module
    to a newly created user, dynamically setting the company
    based on the session's current company.
    Additionally, ensure that all modules are unselected in the Module Profile.
    """
    # Fetch the current logged-in user
    current_user = frappe.session.user

    # Skip execution if the current user is admin@invoix.in
    #if current_user == "admin@invoix.biz":
     #   return

    # Fetch the company dynamically from the session
    company = frappe.defaults.get_user_default("Company")

    # Ensure the company exists
    if not company:
        company = doc.company_name
   # Add User Permission for the new user
    user_permission = frappe.get_doc({
        "doctype": "User Permission",
        "user": doc.name,
        "allow": "Company",  # Doctype for which permission is granted
        "for_value": doc.company_name,  # Company name from the session
        "is_default": 1,  # Mark this permission as default
    })
    user_permission.insert(ignore_permissions=True)  # Insert without permission checks



@frappe.whitelist()
def update_splash_and_app_logo():

    # Get the logged-in user
    user = frappe.session.user
    print("User is ", user)
    if not user:
        frappe.logger().error("No user found in session.")
        return {"success": False, "message": "No user found in session."}

    frappe.logger().info(f"Updating splash and app logo for user: {user}")

    # Fetch the company name from the 'user_company_name' field in the User doctype
    company = frappe.db.get_value("User", user, "company_name")
    print("Company is ", company)
    if not company:
        frappe.logger().info(f"No company linked to user: {user}")
        return {"success": False, "message": f"No company linked to user: {user}"}

    frappe.logger().info(f"Company: {company}")

    # Define a default logo path
    default_logo = "/assets/your_app/images/default-logo.png"

    # Fetch the company logo or use the default logo
    logo = frappe.db.get_value("Company", company, "company_logo")
    print("Logo is ", logo)
    frappe.logger().info(f"Logo: {logo}")

    # Update Website Settings
    website_settings = frappe.get_doc("Website Settings", "Website Settings")
    # website_settings.splash_image = logo
    website_settings.app_logo = logo
    website_settings.save()

    # Ensure changes are committed to the database
    frappe.db.commit()

    # Clear and reload settings into the session
    frappe.cache().delete_value("website_settings")
    frappe.clear_cache()
    frappe.clear_cache(user=user)

    frappe.logger().info("Splash and App Logo updated and reloaded successfully.")
    return {
        "success": True,
        "app_logo": website_settings.app_logo
    }



