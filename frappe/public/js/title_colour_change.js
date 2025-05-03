frappe.standard_pages["Workspaces"] = function () {
    var wrapper = frappe.container.add_page("Workspaces");

    frappe.ui.make_app_page({
        parent: wrapper,
        name: "Workspaces",
        title: __("Workspace"),
    });

    frappe.workspace = new frappe.views.Workspace(wrapper);
    $(wrapper).bind("show", function () {
        frappe.workspace.show();
    });

    // Inject custom CSS
    injectCustomCSS();

    // Apply the custom-text-color class to the title text
    $(wrapper).find(".title-text").addClass("custom-text-color");
}

// Function to inject custom CSS
function injectCustomCSS() {
    const css = `
        .custom-text-color {
            color: darkblue;
        }
    `;
    const style = document.createElement('style');
    style.type = 'text/css';
    if (style.styleSheet) {
        style.styleSheet.cssText = css; // For IE8 and below
    } else {
        style.appendChild(document.createTextNode(css));
    }
    document.head.appendChild(style);
}
