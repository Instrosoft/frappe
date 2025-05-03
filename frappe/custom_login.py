# import json
# from urllib.parse import parse_qs
# import frappe
# from frappe.auth import LoginManager

# class CustomLoginManager(LoginManager):
#     def authenticate(self, user=None, pwd=None):
#         # Attempt to retrieve credentials from parameters or form_dict
#         self.user = user or frappe.form_dict.get('usr')
#         self.password = pwd or frappe.form_dict.get('pwd')

#         # If credentials are not found, attempt to retrieve from raw request data
#         if not self.user or not self.password:
#             try:
#                 raw_data = frappe.request.get_data(as_text=True)
#                 if raw_data:
#                     # Parse the URL-encoded form data
#                     parsed_data = parse_qs(raw_data)
#                     self.user = self.user or parsed_data.get('usr', [None])[0]
#                     self.password = self.password or parsed_data.get('pwd', [None])[0]
#             except Exception as e:
#                 frappe.log_error(f"Error parsing request data: {e}", "CustomLoginManager.authenticate")

#         # Debugging statements to verify retrieved credentials
#         print("Retrieved Username:", self.user)
#         print("Retrieved Password:", self.password)

#         # Ensure both user and password are provided
#         if not self.user or not self.password:
#             self.fail('Incomplete login details')

#         # Extract the subdomain from the request host
#         subdomain = frappe.local.request.host.split('.')[0]
#         print("Subdomain:", subdomain)

#         # Implement subdomain-based access control
#         if subdomain == 'admin':
#             if self.user not in ['admin@invoix.biz', 'Administrator']:
#                 frappe.throw('You do not have the necessary permissions to access this resource. Please contact your administrator if you believe this is an error.')
               
#         elif subdomain == 'app':
#             if self.user in ['admin@invoix.biz', 'Administrator']:
#                 frappe.throw('Access to this section is restricted to standard users. Administrators should log in using the https://admin.invoix.biz/login URL.')

#         # Proceed with standard authentication
#         super(CustomLoginManager, self).authenticate(self.user, self.password)
import json
from urllib.parse import parse_qs
import frappe
from frappe.auth import LoginManager

class CustomLoginManager(LoginManager):
    def authenticate(self, user=None, pwd=None):
        try:
            # Attempt to retrieve credentials from parameters or form_dict
            self.user = user or frappe.form_dict.get('usr')
            self.password = pwd or frappe.form_dict.get('pwd')

            # If credentials are not found, attempt to retrieve from raw request data
            if not self.user or not self.password:
                raw_data = frappe.request.get_data(as_text=True)
                if raw_data:
                    # Parse the URL-encoded form data
                    parsed_data = parse_qs(raw_data)
                    self.user = self.user or parsed_data.get('usr', [None])[0]
                    self.password = self.password or parsed_data.get('pwd', [None])[0]

            # Ensure both user and password are provided
            if not self.user or not self.password:
                self.fail('Incomplete login details')

            # Extract the subdomain from the request host
            subdomain = frappe.local.request.host.split('.')[0]

            # Subdomain-specific access control
            if subdomain == 'admin':
                if self.user not in ['admin@invoix.biz', 'Administrator']:
                    self.terminate_session()
                    frappe.throw('You do not have the necessary permissions to access this resource. Please contact your administrator if you believe this is an error.')

            elif subdomain == 'app':
                if self.user in ['admin@invoix.biz', 'Administrator']:
                    self.terminate_session()
                    frappe.throw('Access to this section is restricted to standard users. Administrators should log in using the https://admin.invoix.biz/login URL.')

            # Proceed with standard authentication
            super(CustomLoginManager, self).authenticate(self.user, self.password)

        except Exception as e:
            frappe.log_error(f"Error during authentication", "CustomLoginManager.authenticate")
            raise

    def terminate_session(self):
        """Forcefully terminate the session if access is denied."""
        frappe.local.login_manager.logout()  # Ensures the current user is logged out
        frappe.db.commit()  # Commit the logout to persist the session termination
