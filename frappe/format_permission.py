# import frappe

# def get_allowed_print_formats(doctype, docname=None):
#     """
#     Overrides allowed print formats for a user, restricting 'Custom Invoix Sales Invoice Format'
#     for all users except 'admin@invoix.biz'.
#     """
#     # Get the current logged-in user
#     user = frappe.session.user

#     # Fetch the list of all print formats for the given doctype
#     print_formats = frappe.get_all(
#         "Print Format",
#         filters={"doc_type": doctype},
#         pluck="name"
#     )

#     # Restrict the specific print format if the user is not authorized
#     if user != "admin@invoix.biz":
#         print_formats = [fmt for fmt in print_formats if fmt != "Custom Invoix Sales Invoice Format"]

#     return print_formats
 