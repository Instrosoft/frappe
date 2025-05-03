from frappe.api.third_party_api import MSDIRECTAPI
import frappe
import json
from datetime import datetime
import base64
from frappe.utils.print_format import download_pdf


# def format_time(time_str):
#     # Parse the time string with microseconds
#     time_obj = datetime.strptime(time_str, "%H:%M:%S.%f")
#     # Format it to match the required format HH:MM:SS
#     return time_obj.strftime("%H:%M:%S")


# data = {
#   "legalEntityId": 331024,
#   "routing": {
#     "eIdentifiers": [
#       {
#         "scheme": "MY:EIF",
#         "id": "01201903094549"
#       }
#     ],
#     "networks": [
#       {
#         "application": "my-lhdnm",
#         "settings": {
#           "enabled": True,
#           "mock": False
#         }
#       }
#     ]
#   },
#   "attachments": [
#     {
#       "filename": "invoice.pdf",
#       "document": "JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDI0MDUyODIyNTY0Ni0wMScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjQwNTI4MjI1NjQ2LTAxJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3BlY2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAxODAKPj4Kc3RyZWFtCkdhcm85XSpjRD8mNFFKRGBAOT4oRztMZFFxPnFnN19ZY1s/X2xTcnE6cGE/cW1rLHEmSmhrNHRPKXNhcWBlVjNCPGw3XCNTSFBAVSxuYHM/MXViSGJob2dQLTBzJF1HWFZraGFEdG0hRkQiRD1XPHEqS2pNTmcqQmc6WnAxZ15kOTo+VzxoNkErWVhSSU1qYmFfW2QoISU9UWssUWBXMFpiZGZdQW1pUiJwIj5AZlEyaUB+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDczIDAwMDAwIG4gCjAwMDAwMDAxMDQgMDAwMDAgbiAKMDAwMDAwMDIxMSAwMDAwMCBuIAowMDAwMDAwNDE0IDAwMDAwIG4gCjAwMDAwMDA0ODIgMDAwMDAgbiAKMDAwMDAwMDc3OCAwMDAwMCBuIAowMDAwMDAwODM3IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDY3ZWM4YTUwZDNiMGVjMDYzNjZjMTY5MDBmZjIxZWUzPjw2N2VjOGE1MGQzYjBlYzA2MzY2YzE2OTAwZmYyMWVlMz5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA1IDAgUgovUm9vdCA0IDAgUgovU2l6ZSA4Cj4+CnN0YXJ0eHJlZgoxMTA3CiUlRU9GCg==",
#       "mimeType": "application/pdf",
#       "primaryImage": True,
#       "documentId": "invoice12345",
#       "description": "Invoice document with {{Long ID}} and {{QR Code}} placeholder tags"
#     }
#   ],
#   "document": {
#     "documentType": "invoice",
#     "invoice": {
#       "taxSystem": "tax_line_percentages",
#       "documentCurrency": "MYR",
#       "invoiceNumber": "INV-SINV-2025-00012",
#       "issueDate": "2025-02-20",
#       "issueTime": "02:01:40",
#       "timeZone": "+0800",
#     # //   "taxPointDate": "",
#       "dueDate": "2025-03-22",
#       "invoicePeriod": "2025-02-20 - 2025-03-22",
#     # //   "references": [
#     # //     {
#     # //       "documentType": "purchase_order",
#     # //       "documentId": "E12345678912"
#     # //     },
#     # //     {
#     # //       "documentType": "my_customs_form_1_9",
#     # //       "documentId": "E23456789123"
#     # //     },
#     # //     {
#     # //       "documentType": "my_customs_form_2",
#     # //       "documentId": "E23456789123"
#     # //     },
#     # //     {
#     # //       "documentType": "certified_exporter_authorization",
#     # //       "documentId": "E.g. ATIGA number"
#     # //     },
#     # //     {
#     # //       "documentType": "free_trade_agreement",
#     # //       "documentId": "Free-trade Agreement Number"
#     # //     }
#     # //   ],
#       "accountingSupplierParty": {
#         "party": {
#           "contact": {
#             "email": "vemalaramaloo@yahoo.com",
#             "firstName": "Vemala",
#             "lastName": "Ramaloo",
#             "phone": "+60-167910674"
#           }
#         }
#       },
#       "accountingCustomerParty": {
#         "party": {
#           "companyName": "MURU ENTERPRISE",
#           "address": {
#             "street1": "NO.62",
#             "street2": "JALAN IPOH",
#             "city": "Perak",
#             "zip": "31050",
#             "county": "MY-14",
#             "country": "MY"
#           },
#           "contact": {
#             "email": "vemalaramaloo@yahoo.com",
#             "firstName": "vemala",
#             "lastName": "ramaloo",
#             "phone": "+60-167910674"
#           }
#         },
#         "publicIdentifiers": [
#           {
#             "scheme": "MY:TIN",
#             "id": "C26032362040"
#           },
#           {
#             "scheme": "MY:EIF",
#             "id": "01201903094549"
#           }
#         # //   {
#         # //     "scheme": "MY:SST",
#         # //     "id": "W00001111111111"
#         # //   }
#         ]
#       },
#     # //   "delivery": {
#     # //     "deliveryParty": {
#     # //       "party": {
#     # //         "companyName": "Greenz Sdn. Bhd.",
#     # //         "address": {
#     # //           "country": "MY"
#     # //         }
#     # //       },
#     # //       "publicIdentifiers": [
#     # //         {
#     # //           "scheme": "MY:TIN",
#     # //           "id": "C58662356060"
#     # //         },
#     # //         {
#     # //           "scheme": "MY:EIF",
#     # //           "id": "01202401123456"
#     # //         }
#     # //       ]
#     # //     },
#     # //     "actualDeliveryDate": "2025-02-23",
#     # //     "deliveryLocation": {
#     # //       "address": {
#     # //         "street1": "Lot 66",
#     # //         "street2": "Bangunan Merdeka",
#     # //         "city": "Kuala Lumpur",
#     # //         "zip": "50480",
#     # //         "county": "MY-14",
#     # //         "country": "MY"
#     # //       }
#     # //     },
#     # //     "shipment": {
#     # //       "originAddress": {
#     # //         "country": "SG"
#     # //       },
#     # //       "allowanceCharges": [
#     # //         {
#     # //           "amountExcludingTax": 1000,
#     # //           "reason": "Shipment charge",
#     # //           "taxesDutiesFees": [
#     # //             {
#     # //               "category": "exempt",
#     # //               "country": "MY",
#     # //               "percentage": 0
#     # //             }
#     # //           ]
#     # //         }
#     # //       ]
#     # //     }
#     # //   },
#     # //   "deliveryTerms": {
#     # //     "incoterms": "EXW"
#     # //   },
#       "paymentTerms": {
#         "note": "Payment within 30 days"
#       },
#       "paymentMeansArray": [
#         {
#           "code": "credit_transfer",
#           "account": "1234567890123",
#           "branche_code": "AAVVVVVV"
#         }
#       ],
#       "invoiceLines": [
#         {
#           "lineId": "1",
#           "amountExcludingVat": 1800,
#           "itemPrice": 17,
#           "baseQuantity": 1,
#           "quantity": 100,
#           "quantityUnitCode": "C62",
#           "allowanceCharges": [
#             {
#               "reason": "Service charge",
#               "amountExcludingTax": 100
#             }
#           ],
#           "tax": {
#             "percentage": 6,
#             "country": "MY",
#             "category": "service"
#           },
#           "references": [
#             {
#               "documentType": "item_classification_code",
#               "documentIdListId": "PTC",
#               "documentId": "123456"
#             },
#             {
#               "documentType": "item_classification_code",
#               "documentIdListId": "CLASS",
#               "documentId": "003"
#             }
#           ],
#           "name": "Laptop Peripherals",
#           "description": "Supply",
#           "additionalItemProperties": [
#             {
#               "name": "Key1",
#               "value": "871690930000222221"
#             },
#             {
#               "name": "SomeOtherKey",
#               "value": "VE HAZERSWOUDE-XXXXX"
#             }
#           ]
#         }
#       ],
#       "allowanceCharges": [
#         {
#           "reason": "Another service charge",
#           "amountExcludingTax": 100,
#           "tax": {
#             "percentage": 6,
#             "country": "MY",
#             "category": "service"
#           }
#         }
#       ],
#       "taxSubtotals": [
#         {
#           "taxableAmount": 1900,
#           "taxAmount": 114,
#           "percentage": 6,
#           "country": "MY",
#           "category": "service"
#         }
#         # // {
#         # //   "taxableAmount": 1000,
#         # //   "taxAmount": 0,
#         # //   "percentage": 0,
#         # //   "country": "MY",
#         # //   "category": "exempt"
#         # // }
#       ],
#       "amountIncludingVat": 2014,
#       "prepaidAmount": 1
#     }
#   }
# }

@frappe.whitelist()
def send_invoice(invoice):
  invoice = frappe.parse_json(invoice)
  MSDIRECTAPI().post(data=json.dumps(get_invoice(invoice)),endpoint="document_submissions",integration_request_service="send_invoice")
    


# def get_invoice(invoice):
#     # company = frappe.get_doc("Company", invoice.owner)
#     # print("*************************** COMPANY ***************************",company)
#     print("*************************** COMPANY ***************************", invoice)
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
#                         "enabled": True,
#                         "mock": False
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
#                             "firstName": "Vemala",
#                             "lastName": "Ramaloo",
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
#                             "county": invoice['custom_state'],
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
#                 "invoiceLines": [
#                     {
#                         "lineId": str(item['idx']),
#                         "amountExcludingVat": item['amount'],
#                         "itemPrice": item['rate'],
#                         "baseQuantity": item['qty'],
#                         "quantity": item['qty'],
#                         # "quantityUnitCode": item['item_code'],
#                         # "allowanceCharges": [
#                         #     {
#                         #         "reason": "Service charge",
#                         #         "amountExcludingTax": 100
#                         #     }
#                         # ],
#                         "tax": {
#                             "percentage": 6,
#                             "country": "MY",
#                             "category": "service"
#                         },
#                         "name": item['item_name'],
#                         "description": item['description'],
#                         # "additionalItemProperties": [
#                         #     {
#                         #         "name": "Key1",
#                         #         "value": "871690930000222221"
#                         #     }
#                         # ]
#                     } for item in invoice['items']
#                 ],
#                 "taxSubtotals": [
#                     {
#                         "taxableAmount": invoice['total'],
#                         "taxAmount": invoice['total'] * 0.06,
#                         "percentage": 6,
#                         "country": "MY",
#                         "category": "service"
#                     }
#                 ],
#                 "amountIncludingVat": invoice['grand_total'],
#                 "prepaidAmount": invoice['base_paid_amount']
#             }
#         }
#     }
#     print("*************************** DATA ***************************", data)
#     return data

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
    
    # Grouping invoice lines by tax rate and category dynamically
    for item in invoice['items']:
        item_tax_detail = invoice["taxes"][0]["item_wise_tax_detail"]
        import json
        tax_details = json.loads(item_tax_detail)
        item_code = item['item_code']
        item_tax_percentage = tax_details.get(item_code, [0, 0])[0]  # [percentage, amount]

        tax_key = (item_tax_percentage, "service", "MY")  # Grouping by tax percentage, category, and country
        taxable_amount = round_two_decimals(item['amount'])
        
        # Accumulate the total taxable amount by grouping
        total_taxable_amount[tax_key] = total_taxable_amount.get(tax_key, 0) + taxable_amount
        tax_amount = round_two_decimals(taxable_amount * (item_tax_percentage / 100))
        total_tax_amount[tax_key] = total_tax_amount.get(tax_key, 0) + tax_amount

        # Build invoice line
        invoice_lines.append({
            "lineId": str(item['idx']),
            "amountExcludingVat": taxable_amount,
            "itemPrice": round_two_decimals(item['rate']),
            "baseQuantity": item['qty'],
            "quantity": item['qty'],
            "tax": {
                "percentage": item_tax_percentage,
                "country": "MY",
                "category": "service"
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
            "name": item['item_name'],
            "description": item['description']
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
       
        "document": {
            "documentType": "invoice",
            "invoice": {
                "taxSystem": "tax_line_percentages",
                "documentCurrency": invoice['currency'],
                "invoiceNumber": invoice['name'],
                "issueDate": invoice['posting_date'],
                "issueTime": format_time(invoice['posting_time']),
                "timeZone": "+0800",
                "dueDate": invoice['custom_payment_due_date'],
                "accountingSupplierParty": {
                    "party": {
                        "contact": {
                            "email": invoice['custom_email'],
                            "firstName": "Vemala",
                            "lastName": "Ramaloo",
                            "phone": invoice['custom_contact_number']
                        }
                    }
                },
                "accountingCustomerParty": {
                    "party": {
                        "companyName": invoice['customer_name'],
                        "address": {
                            "street1": invoice['custom_address_line_1'],
                            "street2": invoice['custom_address_line_2'],
                            "city": invoice['custom_city'],
                            "zip": invoice['custom_postal_code'],
                            "county": get_iso_county(invoice['custom_state']),
                            "country": "MY"
                        },
                        "contact": {
                            "email": invoice['custom_email_address'],
                            "firstName": "vemala",
                            "lastName": "ramaloo",
                            "phone": invoice['custom_contact_number']
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
                    "note": f"Payment within {invoice['custom_payment_due_days']} days"
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
                "prepaidAmount": round_two_decimals(invoice['base_paid_amount'])
            }
        }
    }

    print("*************************** DATA ***************************", data)
    return data

# def get_invoice(invoice):

#   print("\n\n\n\n")
#   print(invoice)
#   print("\n\n\n\n")
#   customer = frappe.get_doc("Customer", invoice.customer)

#   data = {"legalEntityId": 331024,
#   "routing": {
#     "eIdentifiers": [
#       {
#         "scheme": "MY:EIF",
#         "id": "01201903094549"
#       }
#     ],
#     "networks": [
#       {
#         "application": "my-lhdnm",
#         "settings": {
#           "enabled": True,
#           "mock": False
#         }
#       }
#     ]
#   },
#   # "attachments": [
#   #   {
#   #     "filename": "invoice.pdf",
#   #     "document": "JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSCj4+CmVuZG9iagoyIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhIC9FbmNvZGluZyAvV2luQW5zaUVuY29kaW5nIC9OYW1lIC9GMSAvU3VidHlwZSAvVHlwZTEgL1R5cGUgL0ZvbnQKPj4KZW5kb2JqCjMgMCBvYmoKPDwKL0NvbnRlbnRzIDcgMCBSIC9NZWRpYUJveCBbIDAgMCA1OTUuMjc1NiA4NDEuODg5OCBdIC9QYXJlbnQgNiAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VDIC9JbWFnZUkgXQo+PiAvUm90YXRlIDAgL1RyYW5zIDw8Cgo+PiAKICAvVHlwZSAvUGFnZQo+PgplbmRvYmoKNCAwIG9iago8PAovUGFnZU1vZGUgL1VzZU5vbmUgL1BhZ2VzIDYgMCBSIC9UeXBlIC9DYXRhbG9nCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9BdXRob3IgKGFub255bW91cykgL0NyZWF0aW9uRGF0ZSAoRDoyMDI0MDUyODIyNTY0Ni0wMScwMCcpIC9DcmVhdG9yIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgL0tleXdvcmRzICgpIC9Nb2REYXRlIChEOjIwMjQwNTI4MjI1NjQ2LTAxJzAwJykgL1Byb2R1Y2VyIChSZXBvcnRMYWIgUERGIExpYnJhcnkgLSB3d3cucmVwb3J0bGFiLmNvbSkgCiAgL1N1YmplY3QgKHVuc3BlY2lmaWVkKSAvVGl0bGUgKHVudGl0bGVkKSAvVHJhcHBlZCAvRmFsc2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvdW50IDEgL0tpZHMgWyAzIDAgUiBdIC9UeXBlIC9QYWdlcwo+PgplbmRvYmoKNyAwIG9iago8PAovRmlsdGVyIFsgL0FTQ0lJODVEZWNvZGUgL0ZsYXRlRGVjb2RlIF0gL0xlbmd0aCAxODAKPj4Kc3RyZWFtCkdhcm85XSpjRD8mNFFKRGBAOT4oRztMZFFxPnFnN19ZY1s/X2xTcnE6cGE/cW1rLHEmSmhrNHRPKXNhcWBlVjNCPGw3XCNTSFBAVSxuYHM/MXViSGJob2dQLTBzJF1HWFZraGFEdG0hRkQiRD1XPHEqS2pNTmcqQmc6WnAxZ15kOTo+VzxoNkErWVhSSU1qYmFfW2QoISU9UWssUWBXMFpiZGZdQW1pUiJwIj5AZlEyaUB+PmVuZHN0cmVhbQplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDczIDAwMDAwIG4gCjAwMDAwMDAxMDQgMDAwMDAgbiAKMDAwMDAwMDIxMSAwMDAwMCBuIAowMDAwMDAwNDE0IDAwMDAwIG4gCjAwMDAwMDA0ODIgMDAwMDAgbiAKMDAwMDAwMDc3OCAwMDAwMCBuIAowMDAwMDAwODM3IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDY3ZWM4YTUwZDNiMGVjMDYzNjZjMTY5MDBmZjIxZWUzPjw2N2VjOGE1MGQzYjBlYzA2MzY2YzE2OTAwZmYyMWVlMz5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA1IDAgUgovUm9vdCA0IDAgUgovU2l6ZSA4Cj4+CnN0YXJ0eHJlZgoxMTA3CiUlRU9GCg==",
#   #     "mimeType": "application/pdf",
#   #     "primaryImage": True,
#   #     "documentId": "invoice12345",
#   #     "description": "Invoice document with {{Long ID}} and {{QR Code}} placeholder tags"
#   #   }
#   # ],
#   "document": {
#     "documentType": "invoice",
#     "invoice": {
#       "taxSystem": "tax_line_percentages",
#       "documentCurrency": "MYR",
#       "invoiceNumber": invoice.name,
#       "issueDate": "2025-02-20",
#       "issueTime": "02:01:40",
#       "timeZone": "+0800",
 
#       "dueDate": "2025-03-22",
   
#       "accountingSupplierParty": {
#         "party": {
#           "contact": {
#             "email": "vemalaramaloo@yahoo.com",
#             "firstName": "Vemala",
#             "lastName": "Ramaloo",
#             "phone": "+60-167910674"
#           }
#         }
#       },
#       "accountingCustomerParty": {
#         "party": {
#           "companyName": customer.name,
#           "address": {
#             "street1": "NO.62",
#             "street2": "JALAN IPOH",
#             "city": "Perak",
#             "zip": "31050",
#             "county": "MY-14",
#             "country": "MY"
#           },
#           "contact": {
#             "email": "vemalaramaloo@yahoo.com",
#             "firstName": "vemala",
#             "lastName": "ramaloo",
#             "phone": "+60-167910674"
#           }
#         },
#         "publicIdentifiers": [
#           {
#             "scheme": "MY:TIN",
#             "id": "C26032362040"
#           },
#           {
#             "scheme": "MY:EIF",
#             "id": "01201903094549"
#           }
#         # //   {
#         # //     "scheme": "MY:SST",
#         # //     "id": "W00001111111111"
#         # //   }
#         ]
#       },
   
#       "paymentTerms": {
#         "note": f"Payment within {invoice.custom_payment_due_days} days"
#       },
#       "paymentMeansArray": [
#         {
#           "code": "credit_transfer",
#           "account": "1234567890123",
#           "branche_code": "AAVVVVVV"
#         }
#       ],
#       "invoiceLines": [
#         {
#           "lineId": "1",
#           "amountExcludingVat": 1800,
#           "itemPrice": 17,
#           "baseQuantity": 1,
#           "quantity": 100,
#           "quantityUnitCode": "C62",
#           "allowanceCharges": [
#             {
#               "reason": "Service charge",
#               "amountExcludingTax": 100
#             }
#           ],
#           "tax": {
#             "percentage": 6,
#             "country": "MY",
#             "category": "service"
#           },
#           "references": [
#             {
#               "documentType": "item_classification_code",
#               "documentIdListId": "PTC",
#               "documentId": "123456"
#             },
#             {
#               "documentType": "item_classification_code",
#               "documentIdListId": "CLASS",
#               "documentId": "003"
#             }
#           ],
#           "name": "Laptop Peripherals",
#           "description": "Supply",
#           "additionalItemProperties": [
#             {
#               "name": "Key1",
#               "value": "871690930000222221"
#             },
#             {
#               "name": "SomeOtherKey",
#               "value": "VE HAZERSWOUDE-XXXXX"
#             }
#           ]
#         }
#       ],
#       "allowanceCharges": [
#         {
#           "reason": "Another service charge",
#           "amountExcludingTax": 100,
#           "tax": {
#             "percentage": 6,
#             "country": "MY",
#             "category": "service"
#           }
#         }
#       ],
#       "taxSubtotals": [
#         {
#           "taxableAmount": 1900,
#           "taxAmount": 114,
#           "percentage": 6,
#           "country": "MY",
#           "category": "service"
#         }
        
#       ],
#       "amountIncludingVat": 2014,
#       "prepaidAmount": 1
#     }
#   }
#   }
#   return data

