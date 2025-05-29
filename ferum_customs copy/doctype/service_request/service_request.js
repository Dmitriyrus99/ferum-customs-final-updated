frappe.ui.form.on('ServiceRequest', {
    service_object_link: function(frm) {
        frm.set_query('engineer', 'assigned_engineers_table', function() {
            return {
                query: 'ferum_customs.utils.get_engineers_for_service_object',
                filters: {
                    service_object: frm.doc.service_object_link
                }
            };
        });
        frm.add_fetch('service_object_link', 'linked_service_project', 'project');
    }
});
