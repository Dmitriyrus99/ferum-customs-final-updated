frappe.ui.form.on('ServiceRequest', {
    service_object: function(frm) {
        if (!frm.doc.service_object) return;

        frappe.call({
            method: 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object',
            args: { service_object: frm.doc.service_object },
            callback: function(r) {
                frm.set_query('assigned_engineer', function() {
                    return {
                        filters: [['User', 'name', 'in', r.message]]
                    };
                });
            }
        });
    }
});
