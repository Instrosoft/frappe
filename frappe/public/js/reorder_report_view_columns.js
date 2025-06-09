const _setup_columns = frappe.views.ReportView.prototype.setup_columns;

frappe.views.ReportView.prototype.setup_columns = function () {
    _setup_columns.apply(this, arguments);

    if (this.doctype === "Payment Entry") {
        this.fields = [
            ["name", this.doctype],
            ["posting_date", this.doctype],
            ["mode_of_payment", this.doctype],
            ["party_name", this.doctype],
            ["paid_amount", this.doctype],
            ["status", this.doctype],
            ["custom_sales_invoice_single", this.doctype],
        ];
    }   

    if (this.doctype === "Sales Invoice") {
        this.fields = [
            ["name", this.doctype],
            ["customer_name", this.doctype],
            ["posting_date", this.doctype],
            ["grand_total", this.doctype],
            ["outstanding_amount", this.doctype],
            ["due_date", this.doctype],
            ["status", this.doctype],
        ];
    }   
};

