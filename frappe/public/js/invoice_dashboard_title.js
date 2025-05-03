
if (window.location.pathname === "/app/invoice-dashboard") {
    console.log("Invoice Dashboard page detected.");

    // Function to locate and update the title element
    const updateTitle = () => {
        const titleElement = document.querySelector(
            "h3.ellipsis.title-text[title='Invoice Dashboard']"
        );

        if (titleElement) {
            console.log("Title element found. Fetching company name...");

            // Fetch the company name for the logged-in user
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "User",
                    filters: { name: frappe.session.user },
                    fieldname: "company_name",
                },
                callback: function (response) {
                    if (response.message && response.message.company_name) {
                        const companyName = response.message.company_name;

                        // Update the title element
                        titleElement.textContent = companyName;
                        titleElement.setAttribute("title", companyName);
                        console.log(`Title updated to: ${companyName}`);
                    } else {
                        console.error("Company name not found for the user.");
                    }
                },
            });
        } else {
            console.log("Title element not found. Retrying...");
            setTimeout(updateTitle, 500); // Retry after 500ms
        }
    };

    // Call the function to start the title update process
    updateTitle();

    // Monitor DOM changes using MutationObserver
    const observer = new MutationObserver(() => {
        const titleElement = document.querySelector(
            "h3.ellipsis.title-text[title='Invoice Dashboard']"
        );
        if (titleElement && titleElement.textContent === "Invoice Dashboard") {
            console.log("Detected DOM update. Updating title...");
            updateTitle();
        }
    });

    // Observe changes in the body for dynamically added elements
    observer.observe(document.body, { childList: true, subtree: true });
}

