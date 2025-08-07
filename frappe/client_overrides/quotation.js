frappe.ui.form.on("Quotation", {
    refresh(frm) {
        if (frm.doc.status != "Ordered")
            frm.add_custom_button(__("Sales Invoice"), () => {
                frappe.model.open_mapped_doc({

                    method: "frappe.server_overrides.quotation.make_sales_invoice",

                    frm: frm,

                });
            }, __("Create"));
    },
    party_name(frm){
        if(!frm.doc.party_name)
            return;
        frappe.call({
            method:
              "frappe.server_overrides.quotation.get_buyer_type",
            args: {
              customer: frm.doc.party_name,
            },
            callback(r) {
              frm.set_value("custom_buyer_type", r.message)
            },
          });
    },
    async onload(frm) {
      if(frm.doc.company){
        const resp=await frappe.db.get_value("Company",cur_frm.doc.company,"abbr")
        frm.set_value("naming_series",`QTN-${resp.message.abbr}-.YYYY.-.MM.-.####`);
      }
    }
})