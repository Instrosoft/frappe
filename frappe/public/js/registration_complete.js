frappe.router.on("change",async function(){
	const resp = await frappe.xcall("frappe.api.custom_api.get_registration_details",{
	"email":frappe.session.user_email})
		console.log(resp)
if (!resp.custom_registration_complete) {
frappe.msgprint("Please enter the required Merchant details before proceeding.")
frappe.set_route('Form', 'Company', resp.company?.company_name)

}
})

