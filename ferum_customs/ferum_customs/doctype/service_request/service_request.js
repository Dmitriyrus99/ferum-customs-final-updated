// ferum_customs/ferum_customs/doctype/service_request/service_request.js
/**
 * Клиентский скрипт, специфичный для DocType "ServiceRequest".
 */

frappe.ui.form.on('ServiceRequest', {
    onload: function(frm) {
        // console.log("ServiceRequest DocType-specific JS: Form loaded:", frm.docname);
    },

    refresh: function(frm) {
        // console.log("ServiceRequest DocType-specific JS: Form refreshed. Status:", frm.doc.status);

        if (frm.doc.docstatus === 0 && frm.doc.status === "Открыта") { 
            frm.add_custom_button(__('Назначить инженера (SR Specific)'), function() {
                frappe.msgprint(__('Логика назначения инженера, специфичная для формы ServiceRequest...'));
            }, __("Действия"));
        }

        // ИЗМЕНЕНО: frm.doc.customer -> frm.doc.custom_customer
        if (frm.doc.docstatus === 1 && frm.doc.status === "Выполнена") { // Убедитесь, что статус "Выполнена" корректен
             frm.add_custom_button(__('Создать Акт выполненных работ'), function() {
                frappe.new_doc("ServiceReport", {
                    "service_request": frm.doc.name, // Это стандартное поле в ServiceReport, не меняем
                    "customer": frm.doc.custom_customer // ИЗМЕНЕНО. Поле customer в ServiceReport стандартное.
                });
            }, __("Создать"));
        }
    },

    // Пример обработчика для кастомного поля, если нужно
    /*
    custom_priority: function(frm) { // Если бы priority было кастомным полем
        if (frm.doc.custom_priority === "High") {
            frappe.show_alert({
                message: __("Установлен высокий приоритет для заявки!"),
                indicator: "orange"
            });
        }
    },
    */

    validate: function(frm) {
        // console.log("ServiceRequest DocType-specific JS: Client-side validation...");
        return true; 
    }
});