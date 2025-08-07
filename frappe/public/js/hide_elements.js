// const _form_sidebar_make = frappe.ui.form.Sidebar.prototype.make

// console.log("Inside Hide elmenets")
// frappe.ui.form.Sidebar.prototype.make = function () {
// 	_form_sidebar_make.apply(this, arguments)
// 	this.page.sidebar?.remove()
// 	this.refresh()
// }

// const _list_sidebar_make = frappe.views.ListSidebar.prototype.make

// frappe.views.ListSidebar.prototype.make = function () {
// 	_list_sidebar_make.apply(this, arguments)
// 	this.page.sidebar?.remove()
// }

// frappe.views.ListViewSelect.prototype.add_view_to_menu = function () {
// 	this.parent.prevObject?.remove()
// }

//To allow sidebar in ALLOWED_DOCTYPES


const _form_sidebar_make = frappe.ui.form.Sidebar.prototype.make
const ALLOWED_DOCTYPES = ["Item", "Company","User"]
frappe.ui.form.Sidebar.prototype.make = function () {
	_form_sidebar_make.apply(this, arguments)
	if (ALLOWED_DOCTYPES.includes(this.frm.doctype)) return;
	this.page.sidebar?.remove()
	this.refresh()
}

const _list_sidebar_make = frappe.views.ListSidebar.prototype.make

frappe.views.ListSidebar.prototype.make = function () {
	_list_sidebar_make.apply(this, arguments)
	this.page.sidebar?.remove()
}
frappe.views.ListViewSelect.prototype.add_view_to_menu = function () {
	this.parent.prevObject?.remove()
}

frappe.views.ListView.prototype.get_header_html_skeleton = function (left = "") {

	return `

	<header class="level list-row-head text-muted">

	<div class="level-left list-header-subject">

	${left}

	</div>

	</header>

	`;

}

  

frappe.views.ListView.prototype.get_list_row_html_skeleton = function (left = "") {

	return  `
	<div class="list-row-container" tabindex="1">

	<div class="level list-row">

	<div class="level-left ellipsis">

	${left}

	</div>

	</div>

	<div class="list-row-border"></div>

	</div>
	`;

  

}

  

const sort_selector = frappe.ui.SortSelector.prototype.make;

  

frappe.ui.SortSelector.prototype.make = function () {

sort_selector.apply(this, arguments);

this.parent.find(".sort-selector").remove();

}

frappe.router.on('change', function () {
	// If you want to hide the Help and Notification dropdowns on selected you can use the same logic as used to hide and show the search bar
	// and if you want to remove the notifications and help dropdowns from the DOM you can use the following code
	$(".dropdown-help").remove();
	$(".dropdown-notifications").remove();
	$(".navbar .vertical-bar").remove();
	$(".input-group")?.remove();
	
	
	// To hide Search bar in Workspaces and Sales Invoice List and Form
	const current_route = frappe.get_route();
	if(current_route.length==3 && current_route[2]=="Report"){ $(".menu-btn-group")?.show() }
	else { $(".menu-btn-group")?.hide(); }
	// if (current_route[0] === "Workspaces" || current_route[1] === "Sales Invoice" ) {
	// 	$(".input-group")?.hide();
		
	// }
	// else {
	// 	$(".input-group")?.show();
	// }
	

	// if (current_route[1] === "Sales Invoice" || current_route[1] === "Quotation" || current_route[1] === "Payment Entry" || current_route[1] === "Item" || current_route[1] === "Supplier"|| current_route[1] === "Purchase Invoice") {
	// 	console.log($(".page-form"))
	// 	$(".page-form")?.hide();
		
	// }
	// else {
	// 	$(".page-form")?.show().css('display','flex');

	// }

}) 