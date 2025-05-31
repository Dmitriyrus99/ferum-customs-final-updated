// ferum_customs/ferum_customs/doctype/service_request/service_request.js
// (Предполагается, что файл будет переименован и перемещен в каталог DocType)

frappe.ui.form.on('service_request', {
    // Срабатывает при изменении значения в поле "service_object"
    service_object: function(frm) {
        if (frm.doc.service_object) {
            // 1. Получаем инженеров, назначенных на выбранный ServiceObject
            frappe.call({
                // Рекомендуется использовать основной метод, который мы уже определили
                method: 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object',
                args: {
                    service_object_id: frm.doc.service_object // Передаем ID объекта обслуживания
                },
                callback: function(r) {
                    if (r.message) {
                        // Устанавливаем фильтр для поля "assigned_engineer_user" в ServiceRequest
                        // чтобы можно было выбрать только из списка полученных инженеров.
                        frm.set_query('assigned_engineer_user', function() {
                            return {
                                filters: {
                                    'name': ['in', r.message.length > 0 ? r.message : ['NON_EXISTING_USER']] // 'name' это fieldname для User ID
                                }
                            };
                        });
                        // Опционально: если вернулся только один инженер, можно его автоматически установить
                        // if (r.message.length === 1) {
                        //     frm.set_value('assigned_engineer_user', r.message[0]);
                        // } else {
                        //      frm.set_value('assigned_engineer_user', null); // Очистить, если инженеров несколько или нет
                        // }
                    } else {
                        // Если инженеры не найдены или произошла ошибка без r.message
                        frm.set_query('assigned_engineer_user', function() {
                            return {
                                filters: {
                                    'name': ['in', ['NON_EXISTING_USER']] // Нет доступных инженеров
                                }
                            };
                        });
                        frm.set_value('assigned_engineer_user', null); // Очистить поле
                        // frappe.show_alert({message: __('Инженеры для данного объекта обслуживания не найдены.'), indicator: 'info'});
                    }
                },
                error: function(r) {
                    console.error("Ошибка при получении списка инженеров: ", r);
                    frm.set_query('assigned_engineer_user', function() {
                        return {
                             filters: {
                                'name': ['in', ['NON_EXISTING_USER']]
                            }
                        };
                    });
                    frm.set_value('assigned_engineer_user', null);
                    // frappe.show_alert({message: __('Не удалось загрузить список инженеров.'), indicator: 'error'});
                }
            });

            // 2. Автоматическое заполнение поля "Проект" из связанного объекта обслуживания
            // service_object (источник), linked_service_project (поле в ServiceObject), project (целевое поле в ServiceRequest)
            frm.add_fetch('service_object', 'linked_service_project', 'project'); //
        } else {
            // Если поле "service_object" очищено
            frm.set_value('project', null); // Очищаем связанный проект
            frm.set_value('assigned_engineer_user', null); // Очищаем назначенного инженера
            frm.set_query('assigned_engineer_user', null); // Сбрасываем фильтры для поля инженера
        }
        frm.refresh_field('project');
        frm.refresh_field('assigned_engineer_user');
    },

    // Пример: Автоматическое заполнение контактных данных при выборе клиента
    customer: function(frm) {
        if (frm.doc.customer) {
            // Пытаемся получить основной контакт и адрес для клиента
            // Это можно сделать одним frappe.call или несколькими get_value, или через add_fetch, если поля есть в Customer
            frappe.db.get_doc('Customer', frm.doc.customer).then(customer_doc => {
                // Предположим, у клиента есть поля primary_contact и primary_address
                // И эти поля ссылаются на DocTypes Contact и Address соответственно

                # Установка контактного лица (если есть поле primary_contact в Customer)
                # if (customer_doc.primary_contact) {
                #     frm.set_value('contact_person', customer_doc.primary_contact);
                # } else {
                #     frm.set_value('contact_person', null);
                # }

                # Установка адреса (если есть поле primary_address в Customer, и оно - Link to Address)
                # if (customer_doc.primary_address) {
                #      frappe.db.get_doc('Address', customer_doc.primary_address).then(address_doc => {
                #          frm.set_value('address_display', address_doc.address_line1 + (address_doc.address_line2 ? '
' + address_doc.address_line2 : '') + '
' + address_doc.city);
                #      });
                # } else {
                #    frm.set_value('address_display', null);
                # }
            });
        } else {
            frm.set_value('contact_person', null);
            frm.set_value('address_display', null);
            # и другие связанные поля
        }
        frm.refresh_field('contact_person');
        frm.refresh_field('address_display');
    }

    # refresh: function(frm) {
    #     // Логика, выполняемая при каждом обновлении формы
    # }

    # validate: function(frm) {
    #     // Клиентская валидация перед сохранением
    #     if (!frm.doc.subject) {
    #         frappe.msgprint(__("Пожалуйста, укажите тему заявки."));
    #         frappe.validated = false;
    #     }
    # }
});