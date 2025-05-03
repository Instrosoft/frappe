import frappe

def before_delete(self):
		frappe.msgprint("hwyy")
        # Fetch all Quota Usage records linked to this company
		quota_usages = frappe.get_all(
			"Quota usage",
			filters={"company": self.company_name},
			fields=["name"]
		)
		frappe.throw(quota_usages)
		# Delete each associated Quota Usage record
		for quota in quota_usages:
			frappe.delete_doc("Quota usage", quota.name, ignore_permissions=True)