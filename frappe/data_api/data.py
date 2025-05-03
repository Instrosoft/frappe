# from frappe.api.third_party_api import MSDIRECTAPI
# import frappe
# import json
# from datetime import datetime
# import base64
# from frappe.utils.print_format import download_pdf
# import json


# @frappe.whitelist()
# def send_invoice(invoice):
#     invoice = frappe.parse_json(invoice)
#     response = MSDIRECTAPI().post(data=json.dumps(get_invoice(invoice)),endpoint="document_submissions",integration_request_service="send_invoice")
#     response_api =frappe.parse_json(response)
#     print("RESPONSE API", response_api.guid)
#     frappe.db.set_value("Sales Invoice", invoice['name'], "custom_guid",response_api.guid)
#     frappe.db.set_value("Sales Invoice", invoice['name'], "custom_api_status", "Sent for validation")
#     frappe.db.commit()  

    
# @frappe.whitelist(allow_guest=True)
# def webhook_response():
#     print("hereee******************")
#     data = frappe.request.get_data(as_text=True)
#     payload = json.loads(data)
#     sales_invoice = frappe.db.get_value("Sales Invoice",{ "custom_guid": payload["guid"]}, "name")
#     print("sales_invoice", sales_invoice)
#     if sales_invoice:
#         frappe.db.set_value("Sales Invoice", sales_invoice, "custom_api_status", payload['event'])

# def format_time(time_str):
#     from datetime import datetime
#     time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
#     return time_obj.strftime("%H:%M:%S")


# def round_two_decimals(value):
#     return round(value, 2)

# # Mapping for ISO 3166-2:MY codes
# ISO_3166_MY_CODES = {
#     "Johor": "MY-01",
#     "Kedah": "MY-02",
#     "Kelantan": "MY-03",
#     "Melaka": "MY-04",
#     "Negeri Sembilan": "MY-05",
#     "Pahang": "MY-06",
#     "Penang": "MY-07",
#     "Perak": "MY-08",
#     "Perlis": "MY-09",
#     "Selangor": "MY-10",
#     "Terengganu": "MY-11",
#     "Sabah": "MY-12",
#     "Sarawak": "MY-13",
#     "Kuala Lumpur": "MY-14",
#     "Labuan": "MY-15",
#     "Putrajaya": "MY-16"
# }

# # Get the correct ISO code for county
# def get_iso_county(state):
#     return ISO_3166_MY_CODES.get(state, "MY-14")  # Default to Kuala Lumpur if not found



# def get_invoice(invoice):
#     tax_subtotals = []
#     invoice_lines = []
#     total_taxable_amount = {}
#     total_tax_amount = {}
#     user = frappe.get_doc("User", invoice['owner'])
#     print("first Name:", user.first_name, user.last_name)
#     print("Email:", user.email)
#     print("Roles:", [role.role for role in user.roles])
#     print("Last Login:", user.last_login)
#     print("User Image URL:", user.user_image)

#     # Check if taxes exist
#     has_taxes = bool(invoice.get("taxes"))

#     # Grouping invoice lines by tax rate and category dynamically
#     for item in invoice['items']:
#         if has_taxes:
#             item_tax_detail = invoice["taxes"][0]["item_wise_tax_detail"]
#             tax_details = json.loads(item_tax_detail)
#             item_code = item['item_code']
#             item_tax_percentage = tax_details.get(item_code, [0, 0])[0]  # [percentage, amount]
#         else:
#             item_tax_percentage = 0  # No tax applied

#         tax_key = (
#             item_tax_percentage,
#             "service" if has_taxes else "exempt",
#             "MY"
#         )
#         # taxable_amount = round_two_decimals(item['amount'])
#         taxable_amount = round_two_decimals(item['rate'])
#         # Accumulate the total taxable amount by grouping
#         total_taxable_amount[tax_key] = total_taxable_amount.get(tax_key, 0) + taxable_amount
#         tax_amount = round_two_decimals(taxable_amount * (item_tax_percentage / 100))
#         total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

#         # Build invoice line
#         invoice_lines.append({
#             "lineId": str(item['idx']),
#             "amountExcludingVat": taxable_amount,
#             "itemPrice": round_two_decimals(item['rate']),
#             "baseQuantity": item['qty'],
#             "quantity": item['qty'],
#             "tax": {
#                 "percentage": item_tax_percentage,
#                 "country": "MY",
#                 "category": "service" if has_taxes else "exempt"
#             },
#             "references": [
#                 {
#                     "documentType": "item_classification_code",
#                     "documentIdListId": "PTC",
#                     "documentId": "123456"
#                 },
#                 {
#                     "documentType": "item_classification_code",
#                     "documentIdListId": "CLASS",
#                     "documentId": "003"
#                 }
#             ],
#             "name": item['item_name'],
#             "description": item['description']
#         })

#     # Build taxSubtotals based on dynamically calculated totals
#     for (rate, category, country), taxable_amount in total_taxable_amount.items():
#         tax_subtotals.append({
#             "taxableAmount": round_two_decimals(taxable_amount),
#             "taxAmount": round_two_decimals(total_tax_amount[(rate, category, country)]),
#             "percentage": rate,
#             "country": country,
#             "category": category
#         })

#     # Calculate amountIncludingVat dynamically
#     amount_including_vat = round_two_decimals(sum(total_taxable_amount.values()) + sum(total_tax_amount.values()))

#     # Generate invoice data dynamically
#     data = {
#         "legalEntityId": 331024,
#         "routing": {
#             "eIdentifiers": [
#                 {
#                     "scheme": "MY:EIF",
#                     "id": "01201903094549"
#                 }
#             ],
#             "networks": [
#                 {
#                     "application": "my-lhdnm",
#                     "settings": {
#                         "enabled": False,
#                         "mock": True
#                     }
#                 }
#             ]
#         },
#         "document": {
#             "documentType": "invoice",
#             "invoice": {
#                 "taxSystem": "tax_line_percentages",
#                 "documentCurrency": invoice['currency'],
#                 "invoiceNumber": invoice['name'],
#                 "issueDate": invoice['posting_date'],
#                 "issueTime": format_time(invoice['posting_time']),
#                 "timeZone": "+0800",
#                 "dueDate": invoice['custom_payment_due_date'],
#                 "accountingSupplierParty": {
#                     "party": {
#                         "contact": {
#                             "email": invoice['custom_email_address'],
#                             "firstName": user.first_name or "",
#                             "lastName": user.last_name or "",
#                             "phone": invoice['custom_contact_number']
#                         }
#                     }
#                 },
#                 "accountingCustomerParty": {
#                     "party": {
#                         "companyName": invoice['customer_name'],
#                         "address": {
#                             "street1": invoice['custom_address_line_1'],
#                             "street2": invoice['custom_address_line_2'],
#                             "city": invoice['custom_city'],
#                             "zip": invoice['custom_postal_code'],
#                             "county": get_iso_county(invoice['custom_state']),
#                             "country": "MY"
#                         },
#                         "contact": {
#                             "email": invoice['custom_email_address'],
#                             "firstName": "vemala",
#                             "lastName": "ramaloo",
#                             "phone": invoice['custom_contact_number']
#                         }
#                     },
#                     "publicIdentifiers": [
#                         {
#                             "scheme": "MY:TIN",
#                             "id": "C26032362040"
#                         },
#                         {
#                             "scheme": "MY:EIF",
#                             "id": "01201903094549"
#                         }
#                     ]
#                 },
#                 "paymentTerms": {
#                     "note": f"Payment within {invoice['custom_payment_due_days']} days"
#                 },
#                 "paymentMeansArray": [
#                     {
#                         "code": "credit_transfer",
#                         "account": "1234567890123",
#                         "branche_code": "AAVVVVVV"
#                     }
#                 ],
#                 "invoiceLines": invoice_lines,
#                 "taxSubtotals": tax_subtotals,
#                 "amountIncludingVat": amount_including_vat,
#                 "prepaidAmount": round_two_decimals(invoice['base_paid_amount'])
#             }
#         }
#     }
#     print("\n\n ****************************************************data \n\n data", data)
#     return data


# # def get_invoice(invoice):
# #     tax_subtotals = []
# #     invoice_lines = []
# #     total_taxable_amount = {}
# #     total_tax_amount = {}
# #     user = frappe.get_doc("User", invoice['owner'])
# #     print("first Name:", user.first_name, user.last_name)
# #     print("Email:", user.email)
# #     print("Roles:", [role.role for role in user.roles])
# #     print("Last Login:", user.last_login)
# #     print("User Image URL:", user.user_image)
  
# #     # Grouping invoice lines by tax rate and category dynamically
# #     for item in invoice['items']:
# #         item_tax_detail = invoice["taxes"][0]["item_wise_tax_detail"] 
# #         tax_details = json.loads(item_tax_detail)
# #         item_code = item['item_code']
# #         item_tax_percentage = tax_details.get(item_code, [0, 0])[0]  # [percentage, amount]

# #         tax_key = (item_tax_percentage, "service", "MY")  # Grouping by tax percentage, category, and country
# #         taxable_amount = round_two_decimals(item['amount'])
        
# #         # Accumulate the total taxable amount by grouping
# #         total_taxable_amount[tax_key] = total_taxable_amount.get(tax_key, 0) + taxable_amount
# #         tax_amount = round_two_decimals(taxable_amount * (item_tax_percentage / 100))
# #         total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

   
# #         # Build invoice line
# #         invoice_lines.append({
# #             "lineId": str(item['idx']),
# #             "amountExcludingVat": taxable_/ount,
# #             "itemPrice": round_two_decimals(item['rate']),
# #             "baseQuantity": item['qty'],
# #             "quantity": item['qty'],
# #             "tax": {
# #                 "percentage": item_tax_percentage,
# #                 "country": "MY",
# #                 "category": "service"
# #             },
# #             "references": [
# #               {
# #                 "documentType": "item_classification_code",
# #                 "documentIdListId": "PTC",
# #                 "documentId": "123456"
# #               },
# #               {
# #                 "documentType": "item_classification_code",
# #                 "documentIdListId": "CLASS",
# #                 "documentId": "003"
# #               }
# #             ],
# #             "name": item['item_name'],
# #             "description": item['description']
# #         })

# #     # Build taxSubtotals based on dynamically calculated totals
# #     for (rate, category, country), taxable_amount in total_taxable_amount.items():
# #         tax_subtotals.append({
# #             "taxableAmount": round_two_decimals(taxable_amount),
# #             "taxAmount": round_two_decimals(total_tax_amount[(rate, category, country)]),
# #             "percentage": rate,
# #             "country": country,
# #             "category": category
# #         })

# #     # Calculate amountIncludingVat dynamically
# #     amount_including_vat = round_two_decimals(sum(total_taxable_amount.values()) + sum(total_tax_amount.values()))

    
# #     # Generate invoice data dynamically
# #     data = {
# #         "legalEntityId": 331024,
# #         "routing": {
# #             "eIdentifiers": [
# #                 {
# #                     "scheme": "MY:EIF",
# #                     "id": "01201903094549"
# #                 }
# #             ],
# #             "networks": [
# #                 {
# #                     "application": "my-lhdnm",
# #                     "settings": {
# #                         "enabled": False,
# #                         "mock": True
# #                     }
# #                 }
# #             ]
# #         },
       
# #         "document": {
# #             "documentType": "invoice",
# #             "invoice": {
# #                 "taxSystem": "tax_line_percentages",
# #                 "documentCurrency": invoice['currency'],
# #                 "invoiceNumber": invoice['name'],
# #                 "issueDate": invoice['posting_date'],
# #                 "issueTime": format_time(invoice['posting_time']),
# #                 "timeZone": "+0800",
# #                 "dueDate": invoice['custom_payment_due_date'],
# #                 "accountingSupplierParty": {
# #                     "party": {
# #                         "contact": {
# #                             "email": invoice['custom_email'],
# #                             "firstName": user.first_name or "",
# #                             "lastName": user.last_name or "",
# #                             "phone": invoice['custom_contact_number']
# #                         }
# #                     }
# #                 },
# #                 "accountingCustomerParty": {
# #                     "party": {
# #                         "companyName": invoice['customer_name'],
# #                         "address": {
# #                             "street1": invoice['custom_address_line_1'],
# #                             "street2": invoice['custom_address_line_2'],
# #                             "city": invoice['custom_city'],
# #                             "zip": invoice['custom_postal_code'],
# #                             "county": get_iso_county(invoice['custom_state']),
# #                             "country": "MY"
# #                         },
# #                         "contact": {
# #                             "email": invoice['custom_email_address'],
# #                             "firstName": "vemala",
# #                             "lastName": "ramaloo",
# #                             "phone": invoice['custom_contact_number']
# #                         }
# #                     },
# #                     "publicIdentifiers": [
# #                         {
# #                             "scheme": "MY:TIN",
# #                             "id": "C26032362040"
# #                         },
# #                         {
# #                             "scheme": "MY:EIF",
# #                             "id": "01201903094549"
# #                         }
# #                     ]
# #                 },
# #                 "paymentTerms": {
# #                     "note": f"Payment within {invoice['custom_payment_due_days']} days"
# #                 },
# #                 "paymentMeansArray": [
# #                     {
# #                         "code": "credit_transfer",
# #                         "account": "1234567890123",
# #                         "branche_code": "AAVVVVVV"
# #                     }
# #                 ],
# #                 "invoiceLines": invoice_lines,
# #                 "taxSubtotals": tax_subtotals,
# #                 "amountIncludingVat": amount_including_vat,
# #                 "prepaidAmount": round_two_decimals(invoice['base_paid_amount'])
# #             }
# #         }
# #     }
# #     print("\n\n ****************************************************data \n\n data",data)
# #     return data


from frappe.api.third_party_api import MSDIRECTAPI
import frappe
import json,base64
from datetime import datetime
import base64
from frappe.utils.print_format import download_pdf
import json
from frappe.utils import get_date_str,get_time_str
import requests
from frappe.model.workflow import apply_workflow

def get_document_evidence(document_submission_id):
    url = f"https://api.storecove.com/api/v2/document_submissions/{document_submission_id}/evidence/clearing"
    bearer_token = "D8n9T5D1Qp5kfTvV9RR1vSxFV2rYYRXIiFDGaKJqzPk"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

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
    invoice = frappe.parse_json(invoice)
    invoice = frappe.get_doc("Sales Invoice", invoice['name'])
    response = MSDIRECTAPI().post(data=json.dumps(get_invoice(invoice)),endpoint="document_submissions",integration_request_service="send_invoice")
    response_api =frappe.parse_json(response)
    print("RESPONSE API", response_api.guid)
    frappe.db.set_value("Sales Invoice", invoice.name, "custom_guid",response_api.guid)
    frappe.db.set_value("Sales Invoice", invoice.name, "custom_api_status", "Sent for validation")
    frappe.db.set_value("Sales Invoice", invoice.name, "custom_einvoice_status", "Yes")
    frappe.db.commit()  

    
@frappe.whitelist(allow_guest=True)
def webhook_response():
    print("hereee******************")
    data = frappe.request.get_data(as_text=True)
    payload = json.loads(data)
    sales_invoice = frappe.db.get_value("Sales Invoice",{ "custom_guid": payload["guid"]}, "name")
    print("sales_invoice", sales_invoice)
    if sales_invoice:
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_api_status", payload['event'])
    else: 
        return
    if payload['event'] == 'cleared':
        frappe.db.set_value("Sales Invoice", sales_invoice, {"custom_lhdn_comments":"The e-invoice is still awaiting validation from LHDN", "custom_api_status":"Pending"})
    if payload['event'] == "succeeded":
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_lhdn_comments", "")
        result = get_document_evidence(payload["guid"])
        print("API RESULT IS ")
        print(result)
        if result:
            document_id, long_id = result
            # frappe.db.set_value("Sales Invoice", sales_invoice, "custom_long_id", long_id)
            # frappe.db.set_value("Sales Invoice", sales_invoice, "custom_uuid", document_id)
            validation_url = f"https://preprod.myinvois.hasil.gov.my/{document_id}/share/{long_id}"
            print(validation_url)
            frappe.db.set_value("Sales Invoice", sales_invoice, "custom_invoice_url", validation_url)
            frappe.db.set_value("Sales Invoice", sales_invoice, {"custom_long_id":long_id, "custom_uuid": document_id, "workflow_state": "Success", "docstatus": 1, "status": "Submitted"})

    if payload['event'] == "failed":
        frappe.db.set_value("Sales Invoice", sales_invoice, {"workflow_state": "Failed", "custom_lhdn_comments": ""})
        details_str = payload.get("details", "{}")  # Ensure it's a valid string
        details_json = json.loads(details_str)
        failure_message = "Something went wrong"
        if "details" in details_json and isinstance(details_json["details"], list) and len(details_json["details"]) > 0:
            failure_message = details_json["details"][0].get("message")

        # Fallback to details -> message if nested details message is unavailable
        if not failure_message:
            failure_message = details_json.get("message")

        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_validation_failure_reason", failure_message)

@frappe.whitelist(allow_guest=True)
def received_document():
    print("**** *** **** ***** ***** 000000000 ====================>")
    print("received_document")
#     data = frappe.request.get_data(as_text=True)
#     payload = json.loads(data)
#     print(payload)
#     sales_invoice = frappe.db.get_value("Sales Invoice",{"custom_received_guid": payload["document_guid"]}, "name")
#     print("sales_invoice", sales_invoice)
    # if sales_invoice:
        # frappe.db.set_value("Sales Invoice", sales_invoice, "custom_invoice_url", 'https:google.com')

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
    "Putrajaya": "MY-16"
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
            item_tax_percentage = tax_details.get(item_code, [0, 0])[0]  # [percentage, amount]
        else:
            item_tax_percentage = 0  # No tax applied

        tax_key = (
            item_tax_percentage,
            "service" if has_taxes else "exempt",
            "MY"
        )
        taxable_amount = round_two_decimals(item.rate)
        total_taxable_amount[tax_key] = total_taxable_amount.get(tax_key, 0) + taxable_amount
        tax_amount = round_two_decimals(taxable_amount * (item_tax_percentage / 100))
        total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

        # Build invoice line
        invoice_lines.append({
            "lineId": str(item.idx),
            "amountExcludingVat": taxable_amount,
            "itemPrice": round_two_decimals(item.rate),
            "baseQuantity": item.qty,
            "quantity": item.qty,
            "tax": {
                "percentage": item_tax_percentage,
                "country": "MY",
                "category": "service" if has_taxes else "exempt"
            },
            "references": [
                {
                    "documentType": "item_classification_code",
                    "documentIdListId": "PTC",
                    "documentId": "123456"
                },
                {
                    "documentType": "item_classification_code",
                    "documentIdListId": "CLASS",
                    "documentId": "003"
                }
            ],
            "name": item.item_name,
            "description": item.description
        })

    # Build taxSubtotals based on dynamically calculated totals
    for (rate, category, country), taxable_amount in total_taxable_amount.items():
        tax_subtotals.append({
            "taxableAmount": round_two_decimals(taxable_amount),
            "taxAmount": round_two_decimals(total_tax_amount[(rate, category, country)]),
            "percentage": rate,
            "country": country,
            "category": category
        })

    # Calculate amountIncludingVat dynamically
    amount_including_vat = round_two_decimals(sum(total_taxable_amount.values()) + sum(total_tax_amount.values()))

    # Generate invoice data dynamically
    data = {
        "legalEntityId": 331024,
        "routing": {
            "eIdentifiers": [
                {
                    "scheme": "MY:EIF",
                    "id": "01201903094549"
                }
            ],
            "networks": [
                {
                    "application": "my-lhdnm",
                    "settings": {
                        "enabled": True,
                        "mock": False
                    }
                }
            ]
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
                    "party": {
                        "contact": {
                            "email": invoice.custom_email_address,
                            "firstName": user.first_name or "",
                            "lastName": user.last_name or "",
                            "phone": invoice.custom_contact_number
                        }
                    }
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
                            "country": "MY"
                        },
                        "contact": {
                            "email": invoice.custom_email_address,
                            "firstName": "vemala",
                            "lastName": "ramaloo",
                            "phone": invoice.custom_contact_number
                        }
                    },
                    "publicIdentifiers": [
                        {
                            "scheme": "MY:TIN",
                            "id": "C26032362040"
                        },
                        {
                            "scheme": "MY:EIF",
                            "id": "01201903094549"
                        }
                    ]
                },
                "paymentTerms": {
                    "note": f"Payment within {invoice.custom_payment_due_days} days"
                },
                "paymentMeansArray": [
                    {
                        "code": "credit_transfer",
                        "account": "1234567890123",
                        "branche_code": "AAVVVVVV"
                    }
                ],
                "invoiceLines": invoice_lines,
                "taxSubtotals": tax_subtotals,
                "amountIncludingVat": amount_including_vat,
                "prepaidAmount": round_two_decimals(invoice.base_paid_amount)
            }
        }
    }
    
    print("\n\n**************************************************** Data \n\n", data)
    return data


@frappe.whitelist()
def bulk_send_invoice(invoice_names):
    invoice_names = frappe.parse_json(invoice_names)
    for invoice_name in invoice_names:
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        response = MSDIRECTAPI().post(data=json.dumps(get_invoice(invoice)), endpoint="document_submissions",
                                      integration_request_service="send_invoice")
        response_api = frappe.parse_json(response)
        print("RESPONSE API", response_api.guid)
        frappe.db.set_value("Sales Invoice", invoice.name, "custom_guid", response_api.guid)
        frappe.db.set_value("Sales Invoice", invoice.name, "custom_api_status", "Sent for validation")
        frappe.db.commit()

def get_base64(invoice_name):
    pdf_doc = frappe.get_print("Sales Invoice",invoice_name,"Print Sales invoice Format V2",as_pdf=True)
    base64_value = base64.b64encode(pdf_doc).decode('utf-8')
    return base64_value


# def get_invoice(invoice):
#     tax_subtotals = []
#     invoice_lines = []
#     total_taxable_amount = {}
#     total_tax_amount = {}
#     user = frappe.get_doc("User", invoice['owner'])
#     print("first Name:", user.first_name, user.last_name)
#     print("Email:", user.email)
#     print("Roles:", [role.role for role in user.roles])
#     print("Last Login:", user.last_login)
#     print("User Image URL:", user.user_image)
  
#     # Grouping invoice lines by tax rate and category dynamically
#     for item in invoice['items']:
#         item_tax_detail = invoice["taxes"][0]["item_wise_tax_detail"] 
#         tax_details = json.loads(item_tax_detail)
#         item_code = item['item_code']
#         item_tax_percentage = tax_details.get(item_code, [0, 0])[0]  # [percentage, amount]

#         tax_key = (item_tax_percentage, "service", "MY")  # Grouping by tax percentage, category, and country
#         taxable_amount = round_two_decimals(item['amount'])
        
#         # Accumulate the total taxable amount by grouping
#         total_taxable_amount[tax_key] = total_taxable_amount.get(tax_key, 0) + taxable_amount
#         tax_amount = round_two_decimals(taxable_amount * (item_tax_percentage / 100))
#         total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

   
#         # Build invoice line
#         invoice_lines.append({
#             "lineId": str(item['idx']),
#             "amountExcludingVat": taxable_/ount,
#             "itemPrice": round_two_decimals(item['rate']),
#             "baseQuantity": item['qty'],
#             "quantity": item['qty'],
#             "tax": {
#                 "percentage": item_tax_percentage,
#                 "country": "MY",
#                 "category": "service"
#             },
#             "references": [
#               {
#                 "documentType": "item_classification_code",
#                 "documentIdListId": "PTC",
#                 "documentId": "123456"
#               },
#               {
#                 "documentType": "item_classification_code",
#                 "documentIdListId": "CLASS",
#                 "documentId": "003"
#               }
#             ],
#             "name": item['item_name'],
#             "description": item['description']
#         })

#     # Build taxSubtotals based on dynamically calculated totals
#     for (rate, category, country), taxable_amount in total_taxable_amount.items():
#         tax_subtotals.append({
#             "taxableAmount": round_two_decimals(taxable_amount),
#             "taxAmount": round_two_decimals(total_tax_amount[(rate, category, country)]),
#             "percentage": rate,
#             "country": country,
#             "category": category
#         })

#     # Calculate amountIncludingVat dynamically
#     amount_including_vat = round_two_decimals(sum(total_taxable_amount.values()) + sum(total_tax_amount.values()))

    
#     # Generate invoice data dynamically
#     data = {
#         "legalEntityId": 331024,
#         "routing": {
#             "eIdentifiers": [
#                 {
#                     "scheme": "MY:EIF",
#                     "id": "01201903094549"
#                 }
#             ],
#             "networks": [
#                 {
#                     "application": "my-lhdnm",
#                     "settings": {
#                         "enabled": False,
#                         "mock": True
#                     }
#                 }
#             ]
#         },
       
#         "document": {
#             "documentType": "invoice",
#             "invoice": {
#                 "taxSystem": "tax_line_percentages",
#                 "documentCurrency": invoice['currency'],
#                 "invoiceNumber": invoice['name'],
#                 "issueDate": invoice['posting_date'],
#                 "issueTime": format_time(invoice['posting_time']),
#                 "timeZone": "+0800",
#                 "dueDate": invoice['custom_payment_due_date'],
#                 "accountingSupplierParty": {
#                     "party": {
#                         "contact": {
#                             "email": invoice['custom_email'],
#                             "firstName": user.first_name or "",
#                             "lastName": user.last_name or "",
#                             "phone": invoice['custom_contact_number']
#                         }
#                     }
#                 },
#                 "accountingCustomerParty": {
#                     "party": {
#                         "companyName": invoice['customer_name'],
#                         "address": {
#                             "street1": invoice['custom_address_line_1'],
#                             "street2": invoice['custom_address_line_2'],
#                             "city": invoice['custom_city'],
#                             "zip": invoice['custom_postal_code'],
#                             "county": get_iso_county(invoice['custom_state']),
#                             "country": "MY"
#                         },
#                         "contact": {
#                             "email": invoice['custom_email_address'],
#                             "firstName": "vemala",
#                             "lastName": "ramaloo",
#                             "phone": invoice['custom_contact_number']
#                         }
#                     },
#                     "publicIdentifiers": [
#                         {
#                             "scheme": "MY:TIN",
#                             "id": "C26032362040"
#                         },
#                         {
#                             "scheme": "MY:EIF",
#                             "id": "01201903094549"
#                         }
#                     ]
#                 },
#                 "paymentTerms": {
#                     "note": f"Payment within {invoice['custom_payment_due_days']} days"
#                 },
#                 "paymentMeansArray": [
#                     {
#                         "code": "credit_transfer",
#                         "account": "1234567890123",
#                         "branche_code": "AAVVVVVV"
#                     }
#                 ],
#                 "invoiceLines": invoice_lines,
#                 "taxSubtotals": tax_subtotals,
#                 "amountIncludingVat": amount_including_vat,
#                 "prepaidAmount": round_two_decimals(invoice['base_paid_amount'])
#             }
#         }
#     }
#     print("\n\n ****************************************************data \n\n data",data)
#     return data
