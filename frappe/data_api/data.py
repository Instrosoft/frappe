from datetime import datetime
import pytz
from frappe.api.third_party_api import MSDIRECTAPI
import frappe
import json, base64
import base64
import json
from frappe.utils import get_date_str
import requests
import re
from frappe.utils import get_datetime


def get_document_evidence(document_submission_id):
    url = f"https://api.storecove.com/api/v2/document_submissions/{document_submission_id}/evidence/clearing"
    bearer_token = frappe.conf.store_cove_token
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
        return
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
            "Sales Invoice", sales_invoice, "custom_api_status", payload["event"].capitalize()
        )
    else:
        return
    invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice)
    event = payload["event"].lower()
    if event == "cleared" and invoice_doc.custom_buyer_type != "B2C":
        frappe.db.set_value(
            "Sales Invoice",
            sales_invoice,
            {
                "custom_lhdn_comments": "The e-invoice is cleared from LHDN. It is being processed by peppol.",
                "custom_api_status": "Cleared",
            },
        )
    elif event == "cleared" and invoice_doc.custom_buyer_type == "B2C":
        run_success_flow(sales_invoice, payload)
    if event == "succeeded":
        run_success_flow(sales_invoice, payload)

    if event == "failed":
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

def run_success_flow(sales_invoice, payload):
    frappe.db.set_value("Sales Invoice", sales_invoice, "custom_lhdn_comments", "")
    result = get_document_evidence(payload["guid"])
    print("API RESULT IS ")
    print(result)
    if result:
        document_id, long_id = result
        validation_url = (
            f"https://{frappe.conf.store_cove_validation_url}/{document_id}/share/{long_id}"
        )
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



@frappe.whitelist(allow_guest=True)
def received_document():
    print("**** *** **** ***** ***** 000000000 ====================>")
    print("received_document")


def format_time(time_str):
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

def get_malaysia_datetime():
    tz_kuala_lumpur = pytz.timezone("Asia/Kuala_Lumpur")
    return datetime.now(tz_kuala_lumpur)

def to_malaysia_date_str(dt):
    dt = get_datetime(dt)  # convert string or date to datetime
    malaysia = pytz.timezone("Asia/Kuala_Lumpur")
    malaysia_dt = dt.astimezone(malaysia)
    return malaysia_dt.strftime('%Y-%m-%d')

def get_invoice(invoice):
    tax_subtotals = []
    invoice_lines = []
    total_taxable_amount = {}
    total_tax_amount = {}
    user = frappe.get_doc("User", invoice.owner)

    has_taxes = bool(invoice.get("taxes"))
    item_tax_detail = json.loads(invoice.taxes[0].item_wise_tax_detail) if has_taxes else {}

    for item in invoice.items:
        item_code = item.item_code
        item_net_amount = item.net_amount or item.amount
        item_rate = item.rate
        item_qty = item.qty

        if has_taxes:
            tax_info = item_tax_detail.get(item_code, [0, 0])
            tax_percentage = tax_info[0]
            tax_amount = tax_info[1]
        else:
            tax_percentage = 0
            tax_amount = 0

        tax_key = (tax_percentage, "service" if has_taxes else "exempt", "MY")
        total_taxable_amount[tax_key] = total_taxable_amount.get(tax_key, 0) + item_net_amount
        total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

        classification_code = "022"
        if invoice.custom_item_classification:
            match = re.match(r"(\d{3}):", invoice.custom_item_classification.strip())
            if match:
                classification_code = match.group(1)

        invoice_lines.append({
            "lineId": str(item.idx),
            "amountExcludingTax": round_two_decimals(item_net_amount),
            "itemPrice": round_two_decimals(item_rate),
            "baseQuantity": 1,
            "quantity": item_qty,
            "tax": {
                "percentage": tax_percentage,
                "country": "MY",
                "category": "service" if has_taxes else "exempt",
            },
            "references": [
                {
                    "documentType": "item_classification_code",
                    "documentIdListId": "CLASS",
                    "documentId": classification_code,
                },
            ],
            "name": item.item_name,
            "description": item.description,
        })

    for (rate, category, country), taxable_amount in total_taxable_amount.items():
        tax_subtotals.append({
            "taxableAmount": round_two_decimals(taxable_amount),
            "taxAmount": round_two_decimals(total_tax_amount[(rate, category, country)]),
            "percentage": rate,
            "country": country,
            "category": category,
        })

    amount_including_tax = round_two_decimals(
        sum(total_taxable_amount.values()) + sum(total_tax_amount.values())
    )

    customer = frappe.get_doc("Customer", invoice.customer)
    customer_buyer_type = customer.custom_buyer_type
    company = frappe.get_doc("Company", invoice.company)
    malaysia_time = get_malaysia_datetime()

    issue_date = malaysia_time.strftime('%Y-%m-%d')  # Use this for issueDate
    issue_time = malaysia_time.strftime('%H:%M:%S')  # Use this for issueTime
    timezone = "+0800"

    routingEidentifier = []
    if customer_buyer_type == "B2C" and customer.custom_mykadmytenterapassport_nomyprmykas_no:
        routingEidentifier.append({"scheme": "MY:NRIC", "id": customer.custom_mykadmytenterapassport_nomyprmykas_no})
    elif customer_buyer_type != "B2C" and customer.custom_business_registration_number:
        business_type_code = extract_business_type_code(customer.custom_business_type)
        routingEidentifier.append({"scheme": "MY:EIF", "id": f"{business_type_code}{customer.custom_business_registration_number}"})

    accountingCustomerPartyPublicIdentifiers = []
    if customer_buyer_type == "B2C" and customer.custom_tin_number:
        accountingCustomerPartyPublicIdentifiers.append({"scheme": "MY:TIN", "id": customer.custom_tin_number})
    elif customer_buyer_type != "B2C":
        if customer.custom_tin_number:
            accountingCustomerPartyPublicIdentifiers.append({"scheme": "MY:TIN", "id": customer.custom_tin_number})
        if customer.custom_business_registration_number:
            business_type_code = extract_business_type_code(customer.custom_business_type)
            accountingCustomerPartyPublicIdentifiers.append({"scheme": "MY:EIF", "id": f"{business_type_code}{customer.custom_business_registration_number}"})

    data = {
        "legalEntityId": int(company.custom_legal_entity_id),
        "routing": {
            "eIdentifiers": routingEidentifier,
            "networks": [{"application": "my-lhdnm", "settings": {"enabled": True, "mock": False}}],
        },
        "attachments": [{
            "document": get_base64(invoice.name),
            "mimeType": "application/pdf",
            "primaryImage": True,
        }],
        "document": {
            "documentType": "invoice",
            "invoice": {
                "taxSystem": "tax_line_percentages",
                "documentCurrency": invoice.currency,
                "invoiceNumber": invoice.name,
                "issueDate": issue_date,
                "issueTime": issue_time,
                "timeZone": timezone,
                "dueDate": to_malaysia_date_str(invoice.custom_payment_due_date),
                "accountingSupplierParty": {
                    "companyName": company.company_name,
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
                    "publicIdentifiers": accountingCustomerPartyPublicIdentifiers,
                },
                "paymentTerms": {"note": f"Payment within {invoice.custom_payment_due_days} days"},
                "paymentMeansArray": [{
                    "code": "standing_agreement"
                }],
                "invoiceLines": invoice_lines,
                "taxSubtotals": tax_subtotals,
                "amountIncludingTax": amount_including_tax,
                "prepaidAmount": round_two_decimals(invoice.base_paid_amount),
            },
        },
    }

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
    try:
        pdf_doc = frappe.get_print(
            "Sales Invoice", invoice_name, "Sales Invoice Print Format", as_pdf=True
        )
        if not pdf_doc:
            frappe.throw("PDF generation failed.")
        return base64.b64encode(pdf_doc).decode("utf-8")
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_base64 Failed")
        raise


@frappe.whitelist()
def create_legal_entity(company):
    required_fields = (
        "name",
        "custom_address_line_1",
        "custom_company_country",
        "custom_state",
        "custom_city",
        "custom_street_no",
        "custom_postal_code",
        "custom_business_registration_no",
        "custom_msic_code",
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

    business_type_code = ""
    if company.custom_business_type:
        match = re.match(r"(\d{2}):", company.custom_business_type.strip())
        if match:
            business_type_code = match.group(1)
        else:
            frappe.throw(
                "Invalid format for custom_business_type. Expected format: '01: SSM number'."
            )

    data2 = {
        "identifier": f"{business_type_code}{company.custom_business_registration_no}",
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

    # Add MY:ROB identifier
    data4 = {
        "identifier": company.custom_business_registration_no,
        "scheme": "MY:ROB",
        "superscheme": "iso6523-actorid-upis",
    }

    response4 = MSDIRECTAPI().post(
        data=json.dumps(data4),
        endpoint=f"legal_entities/{id}/peppol_identifiers",
        integration_request_service="Create Peppol Identifier",
    )

    response4 = frappe.parse_json(response4)

    if response4.errors:
        error_msg = response4.errors[0].get(
            "details", "Error creating Peppol Identifier"
        )
        if "does not match format" in error_msg:
            error_msg = "Please check the Malaysia e-invoice ID format"
        frappe.throw(error_msg)

    company.db_set("custom_legal_entity_created", 1)

    ## TODO: Add the logic to delete and update  the legal entity in Storecove


def extract_business_type_code(business_type_str):
    match = (
        re.match(r"(\d{2}):", business_type_str.strip()) if business_type_str else None
    )
    return match and match.group(1) or ""


def build_identifier(company, scheme):
    if not company:
        return None

    if scheme == "MY:EIF":
        if not company.custom_business_type or not company.custom_business_registration_no:
            return None
        return f"{extract_business_type_code(company.custom_business_type)}{company.custom_business_registration_no}"

    elif scheme == "MY:TIN":
        if not company.custom_business_tin_no:
            return None
        return company.custom_business_tin_no

    elif scheme == "MY:ROB":
        if not company.custom_business_registration_no:
            return None
        return company.custom_business_registration_no

    return None


def post_identifier(company, scheme, identifier):
    data = {
        "identifier": identifier,
        "scheme": scheme,
        "superscheme": "iso6523-actorid-upis",
    }
    MSDIRECTAPI().post(
        data=json.dumps(data),
        endpoint=f"legal_entities/{company.custom_legal_entity_id}/peppol_identifiers",
        integration_request_service=f"Post Peppol Identifier {scheme}",
    )


def delete_identifier(company, scheme, identifier):
    MSDIRECTAPI().delete(
        endpoint=f"legal_entities/{company.custom_legal_entity_id}/peppol_identifiers/iso6523-actorid-upis/{scheme}/{identifier}",
        integration_request_service=f"Delete Peppol Identifier {scheme}",
    )


@frappe.whitelist()
def update_legal_entity(company, oldCompany):
    required_fields = (
        "name",
        "custom_address_line_1",
        "custom_company_country",
        "custom_state",
        "custom_city",
        "custom_street_no",
        "custom_postal_code",
        "custom_business_registration_no",
        "custom_msic_code",
    )

    for field in required_fields:
        if not company.get(field):
            label = (
                company.meta.get_label(field)
                if hasattr(company.meta, "get_label")
                else field
            )
            frappe.throw(f"{label} is required to update legal entity")

    schemes = ["MY:EIF", "MY:TIN", "MY:ROB"]

    for scheme in schemes:
        new_id = build_identifier(company, scheme)
        old_id = build_identifier(oldCompany, scheme)

        if new_id != old_id:
            if old_id:
                delete_identifier(company, scheme, old_id)
            if new_id:
                post_identifier(company, scheme, new_id)

    company.db_set("custom_legal_entity_created", 1)


@frappe.whitelist()
def delete_legal_entity(doc):
    if not doc.custom_legal_entity_created or not doc.custom_legal_entity_id:
        return

    schemes = ["MY:EIF", "MY:TIN", "MY:ROB"]
    errors = []

    for scheme in schemes:
        identifier = build_identifier(doc, scheme)
        if not identifier:
            continue
        try:
            delete_identifier(doc, scheme, identifier)
        except Exception as e:
            errors.append(f"{scheme}: {str(e)}")

    # Step 2: Abort if identifier deletion failed
    if errors:
        frappe.throw("Could not delete Peppol Identifiers:\n" + "\n".join(errors))

    # Step 3: Delete the legal entity itself
    try:
        MSDIRECTAPI().delete(
            endpoint=f"legal_entities/{doc.custom_legal_entity_id}",
            integration_request_service="Delete Legal Entity",
        )
    except Exception as e:
        frappe.throw(f"Could not delete Legal Entity: {str(e)}")
