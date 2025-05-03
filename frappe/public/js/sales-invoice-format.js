
const _setup_columns = frappe.views.ListView.prototype.setup_columns;

frappe.views.ListView.prototype.setup_columns = function () {
    _setup_columns.apply(this, arguments);

    // Handle Sales Invoice, Quotation, Customer, and Item
    if (["Sales Invoice", "Quotation", "Customer", "Item", "Journal Entry"].includes(this.doctype)) {
        this.columns = reorder_listview_fields(this.doctype, this.columns);
    }
};

// function reorder_listview_fields(doctype, columns) {
//     const get_df = frappe.meta.get_docfield.bind(null, doctype);

//     // Define the custom column order for each doctype
//     const field_orders = {
//         "Sales Invoice": ["name", "title", "posting_date", "grand_total", "status"],
//         "Quotation": ["name", "title", "transaction_date", "grand_total", "status"],
//         "Customer": ["name", "customer_name", "status"],
//         "Item": ["name", "item_name", "item_group", "disabled"] // Add Item fields
//     };

//     const order = field_orders[doctype];
//     const field_order = [];

//     order.forEach((field, index) => {
//         const df = get_df(field);

//         if (field === "name") {
//             // Add ID column (Invoice No./Quotation No./Customer ID/Item ID)
//             field_order.push({
//                 type: "Subject", // Align checkbox with this column
//                 df: { 
//                     label: doctype === "Item" ? "Item ID" : 
//                            doctype === "Customer" ? "Buyer ID" : 
//                            (doctype === "Sales Invoice" ? "Invoice No." : "Quotation No."), 
//                     fieldname: "name" 
//                 }
//             });
//         } else if (field === "title" || field === "item_name") {
//             // Add Buyer Name (Title) or Item Name
//             field_order.push({
//                 type: "Field",
//                 df: { ...df, label: doctype === "Item" ? "Item Name" : "Buyer Name", fieldname: field }
//             });
//         } else if (field === "posting_date" || field === "transaction_date") {
//             // Add Date column
//             field_order.push({
//                 type: "Field",
//                 df: { ...df, label: "Date", fieldname: field }
//             });
//         } else if (field === "grand_total") {
//             // Add Grand Total column
//             field_order.push({
//                 type: "Field",
//                 df: { ...df, label: "Grand Total", fieldname: "grand_total" }
//             });
//         } else if (field === "item_group") {
//             // Add Item Group column
//             field_order.push({
//                 type: "Field",
//                 df: { ...df, label: "Item Group", fieldname: "item_group" }
//             });
//         } else if (field === "disabled" || field === "status") {
//             // Add Status column
//             field_order.push({
//                 type: "Status",
//                 df: { ...df, label: "Status" }
//             });
//         } else {
//             // Other fields
//             field_order.push({
//                 type: "Field",
//                 df: df
//             });
//         }
//     });

//     return field_order;
// }
function reorder_listview_fields(doctype, columns) {
    const get_df = frappe.meta.get_docfield.bind(null, doctype);

    // Define the custom column order for each doctype
    const field_orders = {
        "Sales Invoice": ["name", "title", "posting_date", "grand_total", "status", "custom_api_status","custom_einvoice_status"],
        "Quotation": ["name", "title", "transaction_date", "grand_total", "status"],
        "Customer": ["name", "customer_name", "custom_buyer_type", "custom_email_address", "custom_contact_number", "status"],
        "Item": ["name", "item_name", "item_group", "disabled"], // Add Item fields
        "Journal Entry": ['name', 'custom_vendor_name','title','custom_vendor_invoice_no', 'total_debit', 'status' ]
    };

    if (frappe.session.user === "Administrator" || frappe.session.user === "admin@invoix.biz") {
        field_orders["Sales Invoice"] = ["name", "posting_date","customer_name",  "custom_plan", "grand_total", "custom_email","custom_end_date", "status","custom_api_status","custom_einvoice_status"];
    }
    
   
    const order = field_orders[doctype];
    const field_order = [];

    order.forEach((field, index) => {
        const df = get_df(field);

        if (field === "name") {
            // Add ID column (Invoice No./Quotation No./Customer ID/Item ID)
            field_order.push({
                type: "Subject", // Align checkbox with this column
                df: { 
                    label: doctype === "Item" ? "Item ID" : 
                           doctype === "Customer" ? "Buyer ID" : 
                           (doctype === "Sales Invoice" ? "Invoice No." : "Quotation No."), 
                    fieldname: "name" 
                }
            });
        } else if (field === "title" || field === "item_name") {
            const label = doctype === "Item" ? "Item Name" : doctype == 'Customer' ? "Buyer Name":'Title'
            // Add Buyer Name (Title) or Item Name
            field_order.push({
                type: "Field",
                df: { ...df, label: label, fieldname: field }
            });
        } else if (field === "posting_date" || field === "transaction_date") {
            // Add Date column
            field_order.push({
                type: "Field",
                df: { ...df, label: "Date", fieldname: field }
            });
        } else if (field === "grand_total") {
            // Add Grand Total column
            field_order.push({
                type: "Field",
                df: { ...df, label: "Grand Total", fieldname: "grand_total" }
            });
        } else if (field === "item_group") {
            // Add Item Group column
            field_order.push({
                type: "Field",
                df: { ...df, label: "Item Group", fieldname: "item_group" }
            });
        }
        else if (field === "custom_vendor_invoice_no" || field === "custom_vendor_name" ){
            field_order.push({
                type: "Field",
                df: { ...df, label: field === "custom_vendor_invoice_no" ? "Invoice No" : "Name", fieldname: field }
            });
        }
        else if (field === "disabled" || field === "status") {
            // Add Status column with filter for Sales Invoice
            if (doctype === "Sales Invoice") {
                // Filter out unwanted statuses
                field_order.push({
                    type: "Status",
                    df: { 
                        ...df, 
                        label: "Status", 
                        fieldname: "status",
                        options: ["Unpaid", "Paid", "Overdue"] // Include only desired statuses
                    }
                });
            } else {
                field_order.push({
                    type: "Status",
                    df: { ...df, label: "Status" }
                });
            }
        } else {
            // Other fields
            field_order.push({
                type: "Field",
                df: df
            });
        }
    });

    return field_order;
}
