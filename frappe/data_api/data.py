from frappe.api.third_party_api import MSDIRECTAPI
import frappe
import json, base64
import base64
import json
from frappe.utils import get_date_str
import requests


def get_document_evidence(document_submission_id):
    url = f"https://api.storecove.com/api/v2/document_submissions/{document_submission_id}/evidence/clearing"
    bearer_token = "uM7Hg353lnC_ggQrcM5YGXdvIbP9xBMv2FLxNgMCLk0"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {bearer_token}"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        document_id = data["evidence"]["document_id"]
        long_id = data["evidence"]["long_id"]

        return document_id, long_id

    except requests.exceptions.RequestException as e:
        print(f"Error during API call: {e}")
        return None
    except KeyError as e:
        print(f"Error accessing data in JSON: {e}")
        return None
    except ValueError as e:
        print(f"Error decoding JSON response: {e}")
        return None


@frappe.whitelist()
def send_invoice(invoice):
    response = None
    invoice = frappe.parse_json(invoice)
    invoice = frappe.get_doc("Sales Invoice", invoice["name"])
    try:
        response = MSDIRECTAPI().post(
            data=json.dumps(get_invoice(invoice)),
            endpoint="document_submissions",
            integration_request_service="send_invoice",
        )
    except Exception as e:
        frappe.log(response)
        frappe.log(e)
        pass
    response_api = frappe.parse_json(response)
    # frappe.throw(response_api.errors[0].source)
    if response_api.get("errors"):
        frappe.db.set_value("Sales Invoice", invoice.name, {"workflow_state": "Draft"})
        frappe.db.commit()
        if "MY:TIN" in response_api.errors[0]["source"]:
            frappe.throw("Error: Please check the TIN number")
        else:
            frappe.throw(f"Error: {response_api['errors']}")

    else:
        frappe.db.set_value(
            "Sales Invoice",
            invoice.name,
            {
                "custom_guid": response_api.guid,
                "custom_api_status": "Sent for validation",
                "custom_einvoice_status": "Yes",
            },
        )


@frappe.whitelist(allow_guest=True)
def webhook_response():
    print("hereee******************")
    data = frappe.request.get_data(as_text=True)
    payload = json.loads(data)
    sales_invoice = frappe.db.get_value(
        "Sales Invoice", {"custom_guid": payload["guid"]}, "name"
    )
    print("sales_invoice", sales_invoice)
    if sales_invoice:
        frappe.db.set_value(
            "Sales Invoice", sales_invoice, "custom_api_status", payload["event"]
        )
    else:
        return
    if payload["event"] == "cleared":
        frappe.db.set_value(
            "Sales Invoice",
            sales_invoice,
            {
                "custom_lhdn_comments": "The e-invoice is still awaiting validation from LHDN",
                "custom_api_status": "Pending",
            },
        )
    if payload["event"] == "succeeded":
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_lhdn_comments", "")
        result = get_document_evidence(payload["guid"])
        print("API RESULT IS ")
        print(result)
        if result:
            document_id, long_id = result
            # frappe.db.set_value("Sales Invoice", sales_invoice, "custom_long_id", long_id)
            # frappe.db.set_value("Sales Invoice", sales_invoice, "custom_uuid", document_id)
            validation_url = (
                f"https://preprod.myinvois.hasil.gov.my/{document_id}/share/{long_id}"
            )
            print(validation_url)
            frappe.db.set_value(
                "Sales Invoice", sales_invoice, "custom_invoice_url", validation_url
            )
            frappe.db.set_value(
                "Sales Invoice",
                sales_invoice,
                {
                    "custom_long_id": long_id,
                    "custom_uuid": document_id,
                    "workflow_state": "Success",
                    "docstatus": 1,
                    "status": "Unpaid",
                },
            )

    if payload["event"] == "failed":
        frappe.db.set_value(
            "Sales Invoice",
            sales_invoice,
            {"workflow_state": "Failed", "custom_lhdn_comments": ""},
        )
        details_str = payload.get("details", "{}")  # Ensure it's a valid string
        details_json = json.loads(details_str)
        failure_message = "Something went wrong"
        if (
            "details" in details_json
            and isinstance(details_json["details"], list)
            and len(details_json["details"]) > 0
        ):
            failure_message = details_json["details"][0].get("message")

        # Fallback to details -> message if nested details message is unavailable
        if not failure_message:
            failure_message = details_json.get("message")

        frappe.db.set_value(
            "Sales Invoice",
            sales_invoice,
            "custom_validation_failure_reason",
            failure_message,
        )


@frappe.whitelist(allow_guest=True)
def received_document():
    print("**** *** **** ***** ***** 000000000 ====================>")
    print("received_document")


def format_time(time_str):
    from datetime import datetime

    time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
    return time_obj.strftime("%H:%M:%S")


def round_two_decimals(value):
    return round(value, 2)


# Mapping for ISO 3166-2:MY codes
ISO_3166_MY_CODES = {
    "Johor": "MY-01",
    "Kedah": "MY-02",
    "Kelantan": "MY-03",
    "Melaka": "MY-04",
    "Negeri Sembilan": "MY-05",
    "Pahang": "MY-06",
    "Penang": "MY-07",
    "Perak": "MY-08",
    "Perlis": "MY-09",
    "Selangor": "MY-10",
    "Terengganu": "MY-11",
    "Sabah": "MY-12",
    "Sarawak": "MY-13",
    "Kuala Lumpur": "MY-14",
    "Labuan": "MY-15",
    "Putrajaya": "MY-16",
}


# Get the correct ISO code for county
def get_iso_county(state):
    return ISO_3166_MY_CODES.get(state, "MY-14")  # Default to Kuala Lumpur if not found


def get_invoice(invoice):
    tax_subtotals = []
    invoice_lines = []
    total_taxable_amount = {}
    total_tax_amount = {}
    user = frappe.get_doc("User", invoice.owner)

    print("First Name:", user.first_name, user.last_name)
    print("Email:", user.email)
    print("Roles:", [role.role for role in user.roles])
    print("Last Login:", user.last_login)
    print("User Image URL:", user.user_image)

    # Check if taxes exist
    has_taxes = bool(invoice.get("taxes"))

    # Grouping invoice lines by tax rate and category dynamically
    for item in invoice.items:
        if has_taxes:
            item_tax_detail = invoice.taxes[0].item_wise_tax_detail
            tax_details = json.loads(item_tax_detail)
            item_code = item.item_code
            item_tax_percentage = tax_details.get(item_code, [0, 0])[
                0
            ]  # [percentage, amount]
        else:
            item_tax_percentage = 0  # No tax applied

        tax_key = (item_tax_percentage, "service" if has_taxes else "exempt", "MY")
        taxable_amount = round_two_decimals(item.rate)
        total_taxable_amount[tax_key] = (
            total_taxable_amount.get(tax_key, 0) + taxable_amount
        )
        tax_amount = round_two_decimals(taxable_amount * (item_tax_percentage / 100))
        total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

        # Build invoice line
        invoice_lines.append(
            {
                "lineId": str(item.idx),
                "amountExcludingVat": taxable_amount,
                "itemPrice": round_two_decimals(item.rate),
                "baseQuantity": item.qty,
                "quantity": item.qty,
                "tax": {
                    "percentage": item_tax_percentage,
                    "country": "MY",
                    "category": "service" if has_taxes else "exempt",
                },
                "references": [
                    {
                        "documentType": "item_classification_code",
                        "documentIdListId": "PTC",
                        "documentId": "123456",
                    },
                    {
                        "documentType": "item_classification_code",
                        "documentIdListId": "CLASS",
                        "documentId": "003",
                    },
                ],
                "name": item.item_name,
                "description": item.description,
            }
        )

    # Build taxSubtotals based on dynamically calculated totals
    for (rate, category, country), taxable_amount in total_taxable_amount.items():
        tax_subtotals.append(
            {
                "taxableAmount": round_two_decimals(taxable_amount),
                "taxAmount": round_two_decimals(
                    total_tax_amount[(rate, category, country)]
                ),
                "percentage": rate,
                "country": country,
                "category": category,
            }
        )

    # Calculate amountIncludingVat dynamically
    amount_including_vat = round_two_decimals(
        sum(total_taxable_amount.values()) + sum(total_tax_amount.values())
    )
    customer = frappe.get_doc("Customer", invoice.customer)
    company = frappe.get_doc("Company", invoice.company)
    # Generate invoice data dynamically
    data = {
        "legalEntityId": int(company.custom_legal_entity_id),
        "routing": {
            "eIdentifiers": [
                {"scheme": "MY:EIF", "id": company.custom_malaysia_einvoice_id},
                {"scheme": "MY:TIN", "id": company.custom_business_tin_no},
            ],
            "networks": [
                {
                    "application": "my-lhdnm",
                    "settings": {"enabled": True, "mock": False},
                }
            ],
        },
        "attachments": [
            {
                #   "filename": invoice.name,
                "document": get_base64(invoice.name),
                "mimeType": "application/pdf",
                "primaryImage": True,
                #   "documentId": invoice.name,
                #   "description": "Invoice document with {{Long ID}} and {{QR Code}} placeholder tags"
            }
        ],
        "document": {
            "documentType": "invoice",
            "invoice": {
                "taxSystem": "tax_line_percentages",
                "documentCurrency": invoice.currency,
                "invoiceNumber": invoice.name,
                "issueDate": get_date_str(invoice.posting_date),
                "issueTime": "00:07:59",
                "timeZone": "+0800",
                "dueDate": get_date_str(invoice.custom_payment_due_date),
                "accountingSupplierParty": {
                    "classificationCode": "62010",
                    "party": {
                        "contact": {
                            "email": company.custom_email_address,
                            "firstName": user.first_name or "",
                            "lastName": user.last_name or "",
                            "phone": company.custom_contact_number,
                        }
                    },
                },
                "accountingCustomerParty": {
                    "party": {
                        "companyName": invoice.customer_name,
                        "classificationCode": "62010",
                        "address": {
                            "street1": invoice.custom_address_line_1,
                            "street2": invoice.custom_address_line_2,
                            "city": invoice.custom_city,
                            "zip": invoice.custom_postal_code,
                            "county": get_iso_county(invoice.custom_state),
                            "country": "MY",
                        },
                        "contact": {
                            "email": invoice.custom_email_address,
                            "firstName": customer.customer_name or "",
                            "lastName": "",
                            "phone": customer.custom_contact_number,
                        },
                    },
                    "publicIdentifiers": [
                        {"scheme": "MY:TIN", "id": customer.custom_tin_number},
                        {
                            "scheme": "MY:EIF",
                            "id": customer.custom_business_registration_number,
                        }
                    ],
                },
                "paymentTerms": {
                    "note": f"Payment within {invoice.custom_payment_due_days} days"
                },
                "paymentMeansArray": [
                    {
                        "code": "credit_transfer",
                        "account": "1234567890123",
                        "branche_code": "AAVVVVVV",
                    }
                ],
                "invoiceLines": invoice_lines,
                "taxSubtotals": tax_subtotals,
                "amountIncludingVat": amount_including_vat,
                "prepaidAmount": round_two_decimals(invoice.base_paid_amount),
            },
        },
    }

    print("\n\n**************************************************** Data \n\n", data)
    return data


@frappe.whitelist()
def bulk_send_invoice(invoice_names):
    invoice_names = frappe.parse_json(invoice_names)
    for invoice_name in invoice_names:
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        response = MSDIRECTAPI().post(
            data=json.dumps(get_invoice(invoice)),
            endpoint="document_submissions",
            integration_request_service="send_invoice",
        )
        response_api = frappe.parse_json(response)
        print("RESPONSE API", response_api.guid)
        frappe.db.set_value(
            "Sales Invoice", invoice.name, "custom_guid", response_api.guid
        )
        frappe.db.set_value(
            "Sales Invoice", invoice.name, "custom_api_status", "Sent for validation"
        )
        frappe.db.commit()


def get_base64(invoice_name):
    pdf_doc = frappe.get_print(
        "Sales Invoice", invoice_name, "Print Sales invoice Format V2", as_pdf=True
    )
    base64_value = base64.b64encode(pdf_doc).decode("utf-8")
    return base64_value


@frappe.whitelist()
def create_legal_entity(company):
    required_fields = (
        "name",
        "custom_address_line_1",
        "custom_address_line_2",
        "custom_company_country",
        "custom_state",
        "custom_city",
        "custom_street_no",
        "custom_postal_code",
        "custom_malaysia_einvoice_id",
        "custom_msic_code"
    )

    for field in required_fields:
        if not company.get(field):
            frappe.throw(
                "{0} is required to create legal entity".format(
                    company.meta.get_label(field)
                )
            )

    frappe.msgprint("Creating legal entity for company: " + company.name, alert=True)

    data = {
        "party_name": company.name,
        "line1": company.custom_address_line_1,
        "city": company.custom_city,
        "zip": company.custom_postal_code,
        "country": "MY",
        "line2": company.custom_address_line_2,
        "county": ISO_3166_MY_CODES.get(company.custom_state, "MY-14"),
        "tenant_id": "",
        "public": True,
        "advertisements": ["invoice"],
        # "third_party_username": null,
        # "third_party_password": null,
        "acts_as_sender": True,
        "acts_as_receiver": True,
        "classification_code": company.custom_msic_code,
        "tax_registered": True,
        "override_own_credentials": True,
        "peppol_identifiers": [],
    }

    response = MSDIRECTAPI().post(
        data=json.dumps(data),
        endpoint="legal_entities",
        integration_request_service="Create Legal Entity",
    )

    response = frappe.parse_json(response)

    if response.errors:
        error_msg = response.errors[0].get("details", "Error creating legal entity")
        frappe.throw(error_msg)

    frappe.msgprint("Legal entity created successfully!")

    id = response.id
    company.db_set("custom_legal_entity_id", id)

    data2 = {
        "identifier": company.custom_malaysia_einvoice_id,
        "scheme": "MY:EIF",
        "superscheme": "iso6523-actorid-upis",
    }

    response2 = MSDIRECTAPI().post(
        data=json.dumps(data2),
        endpoint=f"legal_entities/{id}/peppol_identifiers",
        integration_request_service="Create Peppol Identifier",
    )

    response2 = frappe.parse_json(response2)

    if response2.errors:
        error_msg = response2.errors[0].get(
            "details", "Error creating Peppol Identifier"
        )
        if "does not match format" in error_msg:
            error_msg = "Please check the Malaysia e-invoice ID format"
        frappe.throw(error_msg)

    data3 = {
        "identifier": company.custom_business_tin_no,
        "scheme": "MY:TIN",
        "superscheme": "iso6523-actorid-upis",
    }

    response3 = MSDIRECTAPI().post(
        data=json.dumps(data3),
        endpoint=f"legal_entities/{id}/peppol_identifiers",
        integration_request_service="Create Peppol Identifier",
    )

    response3 = frappe.parse_json(response3)

    if response3.errors:
        error_msg = response3.errors[0].get(
            "details", "Error creating Peppol Identifier"
        )
        if "does not match format" in error_msg:
            error_msg = "Please check the Malaysia e-invoice ID format"

        frappe.throw(error_msg)

    company.db_set("custom_legal_entity_created", 1)
