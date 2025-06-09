import frappe
import os,json

from frappe.data_api.data import create_legal_entity

# def create_template(company, doctype):
#     CURR_DIR = os.path.abspath(os.path.dirname(__file__))
#     JSON_FILE_NAME = os.path.join(CURR_DIR,"tax_template.json")
#     with open(JSON_FILE_NAME, "r") as file:
#             sample_templates = json.load(file)
#     for template in sample_templates:
#         taxes = template.get("taxes", [])
#         for tax in taxes:
#             # Resolve account head based on the provided account name
#             account_name = tax["account"]
#             account = frappe.get_value(
#                 "Account",
#                 {"account_name": account_name, "company": company},
#                 "name"
#             )

#             if not account:
#                 frappe.throw(f"Account {account_name} not found for company {company}")

#             tax["account_head"] = account

#         # Create the Sales or Purchase Taxes and Charges Template document
#         doc = frappe.new_doc(doctype)
#         doc.title = template["title"]
#         doc.is_default = template["is_default"]
#         doc.disabled = template["disabled"]
#         doc.company = company
#         doc.taxes = taxes
#         doc.insert()
def create_template(company, doctype):
    CURR_DIR = os.path.abspath(os.path.dirname(__file__))
    JSON_FILE_NAME = os.path.join(CURR_DIR, "tax_template.json")
    with open(JSON_FILE_NAME, "r") as file:
        sample_templates = json.load(file)
    
    for template in sample_templates:
        taxes = template.get("taxes", [])
        updated_taxes = []
        
        for tax in taxes:
            # Resolve account head based on the provided account name
            account_name = tax["account"]
            account = frappe.get_value(
                "Account",
                {"account_name": account_name, "company": company},
                "name"
            )

            if not account:
                frappe.throw(f"Account {account_name} not found for company {company}")

            tax["account_head"] = account
            updated_taxes.append(tax)  # Collect updated tax dictionaries

        # Create the Sales or Purchase Taxes and Charges Template document
        doc = frappe.new_doc(doctype)
        doc.update({
            "title": template["title"],
            "is_default": template["is_default"],
            "disabled": template["disabled"],
            "company": company,
            "taxes": updated_taxes  # Directly assign updated list of dictionaries
        })
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_permissions = True
        doc.insert()


def create_account(company, doctype):
    CURR_DIR = os.path.abspath(os.path.dirname(__file__))
    JSON_FILE_NAME = os.path.join(CURR_DIR,"tax_account_head_template.json")
    with open(JSON_FILE_NAME, "r") as file:
            sample_templates = json.load(file)
    for template in sample_templates:
        doc = frappe.new_doc(doctype)
        doc.update(template)
        doc.company = company.company_name
        doc.parent_account = template["parent_account"]+ " - " + company.abbr
        doc.flags.ignore_mandatory = True
        doc.flags.ignore_permissions = True
        doc.insert()
        


def on_update(doc, method=None):
    if doc.get("_is_new"):
        create_account(doc,"Account")
        create_template(doc.company_name, "Sales Taxes and Charges Template")
        create_template(doc.company_name, "Purchase Taxes and Charges Template")
        sales_invoice_naming_series_property_setter = get_options_property_setter(
        "Sales Invoice","naming_series",f"INV-{doc.abbr}-.YYYY.-.MM.-.####")
        frappe.make_property_setter(sales_invoice_naming_series_property_setter, validate_fields_for_doctype=False)

        quotation_naming_series_property_setter = get_options_property_setter(
        "Quotation","naming_series",f"QTN-{doc.abbr}-.YYYY.-.MM.-.####")
        frappe.make_property_setter(quotation_naming_series_property_setter, validate_fields_for_doctype=False)

        payment_entry_naming_series_property_setter = get_options_property_setter(
        "Payment Entry","naming_series",f"OR-{doc.abbr}-.YYYY.-.MM.-.####")
        frappe.make_property_setter(payment_entry_naming_series_property_setter, validate_fields_for_doctype=False)

    if doc.custom_legal_entity_created:
        return
    
    create_legal_entity(doc)

# Example setup for the accounts (to be created manually or via a script in ERPNext 15)
def setup_accounts():
    accounts = [
        {"account_name": "Malaysia Tourism Tax", "parent_account": "Duties and Taxes", "account_type": "Tax", "rate": 10},
        {"account_name": "Malaysia SST Sales Tax", "parent_account": "Duties and Taxes", "account_type": "Tax", "rate": 0},
        {"account_name": "Malaysia SST Service Tax", "parent_account": "Duties and Taxes", "account_type": "Tax", "rate": 0},
    ]

    for acc in accounts:
        if not frappe.db.exists("Account", {"account_name": acc["account_name"]}):
            doc = frappe.new_doc("Account")
            doc.account_name = acc["account_name"]
            doc.parent_account = acc["parent_account"]
            doc.account_type = acc["account_type"]
            doc.is_group = 0
            doc.flags.ignore_mandatory = True
            doc.insert()
            frappe.db.commit()


def before_validate(doc,method=None):
    doc._is_new = doc.is_new()
# def before_validate(doc, method=None):
#     if doc.is_new():
#         doc._is_new = True


def get_options_property_setter(doctype, fieldname, new_options, prepend=False):
    existing_options = frappe.get_meta(doctype).get_options(fieldname).split("\n")

    if isinstance(new_options, str):
        new_options = new_options.split("\n")

    if prepend:
        options = new_options + existing_options
    else:
        options = existing_options + new_options

    options = "\n".join(dict.fromkeys(options))

    return {
        "doctype": doctype,
        "fieldname": fieldname,
        "property": "options",
        "value": options,
    }
