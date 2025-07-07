import frappe, requests


@frappe.whitelist(allow_guest=True, methods=["POST"])
def create_company(args):
    """
    Create a new Company in Frappe.
    """
    try:
        # Create a new Company document
        args = frappe.parse_json(args)
        company = frappe.new_doc("Company")
        company.update(args)
        company.custom_subscription_plan = args["custom_subcription_plan"]
        company.custom_payment_mode = args["custom_payment_mode"]
        company.custom_amount_paid = args["custom_amount_paid"]
        company.custom_enable_einvoicing = args["custom_enable_einvoicing"]
        company.save(ignore_mandatory=True, ignore_permissions=True)
        # Make custom_enable_einvoicing readonly after saving
        frappe.db.set_value(
            "Company",
            company.name,
            "custom_enable_einvoicing_read_only",
            1,
            update_modified=False
        )
        return {"status": "success", "message": "Company created successfully."}
    except Exception as e:
        frappe.log_error(title="Create Company Error", message=frappe.get_traceback())
        return {"status": "error", "message": str(e)}


@frappe.whitelist(allow_guest=True)
def create_user(args):
    """
    Create a new User and assign them the 'Admin Accounts' role.
    """
    try:
        args = frappe.parse_json(args)
        user = frappe.new_doc("User")
        user.update(args)
        user.company_name = args["company_name"]
        user.role_profile_name = "Admin Accounts"
        user.insert(ignore_mandatory=True, ignore_permissions=True)
        return {
            "status": "success",
            "message": f"User created and assigned 'Admin Accounts' role successfully.",
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create User Error")
        return {"status": "error", "message": str(e)}



@frappe.whitelist(allow_guest=True)
def main(args):
    create_company(args)
    create_user(args)
    return True


@frappe.whitelist(allow_guest=True)
def get_registration_details(email):
    """
    Get the company name associated with a user email and check if registration is complete.

    :param email: User email to fetch the associated company and registration data.
    :return: Dictionary with registration status and company data.
    """
    if not email:
        frappe.throw("Email is required.")

    # Ignore specific users
    if email in ["admin@invoix.biz", "admin@example.com"]:
        return {
            "custom_registration_complete": 1,  # fieldname mismatch in js
            "company": None,
            "message": "This user is not applicable for registration checks.",
        }

    # Get the company name from the User doctype
    user_data = frappe.db.get_value("User", {"email": email}, ["company_name"])
    if not user_data or not user_data[0]:
        frappe.throw(f"No company associated with the user email: {email}")

    company_name = user_data

    # Get company registration details
    company_data = frappe.db.get_value(
        "Company",
        {"company_name": company_name},
        [
            "name as company_name",
            "custom_business_registration_no",
            "custom_business_tin_no",
            "custom_msic_code",
            "custom_street_no",
            "custom_address_line_1",
            "custom_company_country",
            "custom_state",
            "custom_city",
            "custom_postal_code",
            "custom_email_address",
        ],
        as_dict=True,
    )

    if not company_data:
        frappe.throw(f"No data found for the company: {company_name}")

    # Check if registration is complete (all fields are filled)
    required_fields = [
        "custom_business_registration_no",
        "custom_street_no",
        "custom_address_line_1",
        "custom_company_country",
        "custom_state",
        "custom_city",
        "custom_postal_code",
        "custom_email_address",
    ]

    registration_complete = all(company_data.get(field) for field in required_fields)
    return {
        "custom_registration_complete": 1 if registration_complete else 0,
        "company": company_data,
    }
