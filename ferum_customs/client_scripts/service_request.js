// ferum_customs/client_scripts/service_request.js
// This script is likely bundled via build.json
// Ensure ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object is whitelisted in hooks.py

frappe.ui.form.on('service_request', {
    // This 'service_object' fieldname should exist in service_request DocType
    service_object_link: function(frm) { // Assuming fieldname is service_object_link as per DocType JSON
        if (!frm.doc.service_object_link) {
            // Clear dependent fields if service_object_link is cleared
            // frm.set_value('assigned_engineer', null); // Example
            // frm.set_query('assigned_engineer', null); // Clear previous query
            return;
        }

        frappe.call({
            method: 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object',
            args: { service_object: frm.doc.service_object_link },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    // Assuming 'assigned_engineer' is a Link field to User in service_request,
                    // or a field within a child table where you want to filter engineers.
                    // This example assumes 'assigned_engineer' is a direct Link field in service_request.
                    // If 'assigned_engineer' is in a child table, the set_query target needs adjustment.
                    // e.g. frm.set_query('engineer_field_in_child_table', 'child_table_name', function() { ... })
                    frm.set_query('assigned_engineer', function() { // Ensure 'assigned_engineer' is a field in service_request
                        return {
                            filters: [['User', 'name', 'in', r.message]]
                        };
                    });
                } else {
                    // No engineers found, perhaps clear the query or set a default message
                     frm.set_query('assigned_engineer', function() {
                        return {
                            filters: [['User', 'name', 'in', []]] // effectively no options
                        };
                    });
                    // frm.set_value('assigned_engineer', null); // Clear if no options
                    // frappe.show_alert({message: __('No engineers found for this service object'), indicator: 'info'});
                }
            },
            error: function(r) {
                // Handle error
                console.error("Error fetching engineers: ", r);
                // frappe.show_alert({message: __('Error fetching engineers.'), indicator: 'error'});
            }
        });

        // The following is from ferum_customs/ferum_customs/doctype/service_request/service_request.js
        // It seems more appropriate for DocType specific JS.
        // If 'assigned_engineers_table' is a child table in service_request
        // And 'engineer' is a field in that child table.
        frm.set_query('engineer', 'assigned_engineers_table', function() {
            if (frm.doc.service_object_link) {
                return {
                    // This query 'ferum_customs.utils.get_engineers_for_service_object' needs to exist
                    // and be a whitelisted Python function.
                    query: 'ferum_customs.utils.get_engineers_for_service_object', // This utils path needs to be valid.
                    filters: {
                        service_object: frm.doc.service_object_link
                    }
                };
            }
            return {}; // Return empty if no service_object_link
        });
        // Ensure 'project' is a field in service_request DocType
        // Ensure 'linked_service_project' is a field in ServiceObject DocType
        frm.add_fetch('service_object_link', 'linked_service_project', 'project');
    }
});