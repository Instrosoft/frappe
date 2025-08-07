import frappe
from frappe import _
from frappe.utils import flt, cint
from frappe.contacts.doctype.address.address import get_company_address
from frappe.model.mapper import get_mapped_doc
from frappe.model.utils import get_fetch_values

from erpnext.accounts.party import get_party_account
from erpnext.setup.doctype.item_group.item_group import get_item_group_defaults
from erpnext.stock.doctype.item.item import get_item_defaults
from erpnext.selling.doctype.quotation.quotation import _make_customer

@frappe.whitelist()
def get_buyer_type(customer):
    return frappe.db.get_value("Customer", customer, "custom_buyer_type")

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, ignore_permissions=False):
    customer = _make_customer(source_name, ignore_permissions)
    
    def postprocess(source, target):
        set_missing_values(source, target)
        # Get the advance paid Journal Entries in Sales Invoice Advance
        if target.get("allocate_advances_automatically"):
            target.set_advances()

    def set_missing_values(source, target):
        target.customer = customer.name
        target.custom_buyer_type = frappe.db.get_value("Customer", customer.name, "custom_buyer_type")
        target.customer_name = customer.customer_name
        target.flags.ignore_permissions = True
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")
        target.run_method("set_use_serial_batch_fields")

        if source.company_address:
            target.update({"company_address": source.company_address})
        else:
            # set company address
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(
                get_fetch_values(
                    "Sales Invoice", "company_address", target.company_address
                )
            )

        target.debit_to = get_party_account("Customer", customer.name, source.company)

    def update_item(source, target, source_parent):
        target.amount = flt(source.amount) 
        target.base_amount = target.amount * flt(source_parent.conversion_rate)
        target.qty = (
            target.amount / flt(source.rate)
            if (source.rate)
            else source.qty - source.returned_qty
        )

        if target.item_code:
            item = get_item_defaults(target.item_code, source_parent.company)
            item_group = get_item_group_defaults(
                target.item_code, source_parent.company
            )
            cost_center = item.get("selling_cost_center") or item_group.get(
                "selling_cost_center"
            )

            if cost_center:
                target.cost_center = cost_center

    doclist = get_mapped_doc(
        "Quotation",
        source_name,
        {
            "Quotation": {
                "doctype": "Sales Invoice",
                "field_map": {
                    "party_account_currency": "party_account_currency",
                    "payment_terms_template": "payment_terms_template",
                },
                "field_no_map": ["payment_terms_template"],
                "validation": {"docstatus": ["=", 1]},
            },
            "Quotation Item": {
                "doctype": "Sales Invoice Item",
                "field_map": {
                    "name": "quotation_item",
                    "parent": "prevdoc_docname",
                },
                "postprocess": update_item,
            },
            "Sales Taxes and Charges": {
                "doctype": "Sales Taxes and Charges",
                "reset_value": True,
            },
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
			"Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
        },
        target_doc,
        postprocess,
        ignore_permissions=ignore_permissions,
    )

    automatically_fetch_payment_terms = cint(
        frappe.db.get_single_value(
            "Accounts Settings", "automatically_fetch_payment_terms"
        )
    )
    if automatically_fetch_payment_terms:
        doclist.set_payment_schedule()

    return doclist
