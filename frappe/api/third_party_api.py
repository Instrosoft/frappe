import json
from urllib.parse import urljoin

import requests

import frappe
from frappe import _

# TODO: Replace with actual base URL
BASE_URL = "https://api.storecove.com/api/v2"

# TODO: Replace with actual token
TOKEN = frappe.conf.store_cove_token

ALLOWED_METHODS = frozenset(("POST", "GET", "PATCH", "PUT", "DELETE"))
SENSITIVE_INFO = frozenset(("Authorization",))


class MSDIRECTAPI:
    API_NAME = ""

    def __init__(self):
        self.default_headers = {
            "Content-Type": "application/json",
        }
        self.default_log_values = {}
        self.base_path = ""

    def post(self, *args, **kwargs):
        return self._make_request("POST", *args, **kwargs)

    def get(self, *args, **kwargs):
        return self._make_request("GET", *args, **kwargs)
    
    def delete(self, *args, **kwargs):
        return self._make_request("DELETE", *args, **kwargs)

    def _make_request(
        self,
        method,
        endpoint="",
        params=None,
        headers=None,
        data=None,
        integration_request_service=None,
    ):
        if method not in ALLOWED_METHODS:
            frappe.throw(_("Invalid method {0}").format(method))

        self.set_auth_token()

        url = self.get_url(endpoint)
        request_args = frappe._dict(
            url=url,
            params=params,
            headers={
                **self.default_headers,
                **(headers or {}),
            },
        )

        log_data = {"url": url, "params": params, "data": data}

        log = frappe._dict(
            **self.default_log_values,
            data=log_data,
            integration_request_service=integration_request_service,
            request_headers=request_args.headers.copy(),
        )

        if data:
            request_args.data = data

        response_json = None

        try:
            response = requests.request(method, **request_args)
            frappe.log(response.content)
            try:
                response_json = response.content.decode("utf-8")
                
                # print(type(response.json()))
             
                # response_json = response.json(object_hook=frappe._dict)
                # response_json = json.loads(response_text)
                
            except Exception:
                if not response.content:
                    return
                if not response_json:
                    frappe.throw(_("Error parsing response: {0}").format(response.content))


            # Expect all successful responses to be JSON
            if not response_json:
                if not response.content:
                    return
                frappe.throw(_("Error parsing response: {0}").format(response.content))

            return response_json

        except Exception as e:
            log.error = str(e)
            raise e

        finally:
            if response_json:
                log.output = json.dumps(response_json)

            self.mask_sensitive_info(log)
            enqueue_integration_request(**log)

    def handle_http_code(self, status_code):
        if status_code == 401:
            frappe.throw(_("Unauthorized. Please check your credentials"))

    def get_url(self, endpoint):
        return urljoin(
            BASE_URL,
            "/".join(["v2",endpoint]),
        )

    def set_auth_token(self):
        self.default_headers["Authorization"] = f"Bearer {TOKEN}"

    def mask_sensitive_info(self, log):
        placeholder = "*****"

        for key in SENSITIVE_INFO:
            if key in log.request_headers:
                log.request_headers[key] = placeholder


def enqueue_integration_request(**kwargs):
    #TODO: Replace with actual function
    frappe.enqueue(
        "frappe.api.third_party_api.create_integration_request",
        **kwargs,
    )


def create_integration_request(
    url=None,
    request_id=None,
    request_headers=None,
    data=None,
    output=None,
    error=None,
    reference_doctype=None,
    reference_name=None,
    integration_request_service=None,
    **kwargs,
):
    return frappe.get_doc(
        {
            "doctype": "Integration Request",
            "request_id": request_id,
            "url": url,
            "request_headers": pretty_json(request_headers),
            "data": pretty_json(data),
            "output": pretty_json(output),
            "error": pretty_json(error),
            "status": "Failed" if error else "Completed",
            "reference_doctype": reference_doctype,
            "reference_docname": reference_name,
            "integration_request_service": integration_request_service,
            **kwargs,
        }
    ).insert(ignore_permissions=True)


def pretty_json(obj):
    if not obj:
        return ""

    if isinstance(obj, str):
        return obj

    return frappe.as_json(obj, indent=4)
