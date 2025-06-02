// ferum_customs/public/js/ferum_customs/service_request.js
/**
 * Общий клиентский скрипт для формы "ServiceRequest".
 * Этот скрипт включается в бандл ferum_customs.bundle.js
 * и применяется ко всем формам ServiceRequest.
 *
 * Убедитесь, что Python-метод
 * 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object'
 * добавлен в whitelist в hooks.py вашего приложения.
 */

frappe.ui.form.on('ServiceRequest', {
    /**
     * Обработчик изменения поля 'service_object_link'.
     * При изменении объекта обслуживания:
     * 1. Запрашивает с сервера список инженеров, назначенных на этот объект.
     * 2. Устанавливает динамический фильтр для поля 'assigned_engineer'.
     * 3. Очищает поле 'assigned_engineer', если объект не выбран или инженеры не найдены.
     *
     * @param {object} frm - Объект текущей формы (Form).
     */
    // TODO: Verify fieldname 'service_object_link' in ServiceRequest DocType JSON.
    // TODO: Verify fieldname 'assigned_engineer' in ServiceRequest DocType JSON.
    service_object_link: function(frm) {
        const engineer_field = 'assigned_engineer'; // Предполагаемое имя поля инженера

        if (!frm.doc.service_object_link) {
            // Очищаем поле инженера и его фильтры, если объект обслуживания не выбран.
            frm.set_value(engineer_field, null);
            frm.set_query(engineer_field, null); // Сбрасываем предыдущие фильтры
            frm.refresh_field(engineer_field);
            // add_fetch сам очистит 'project', если service_object_link пуст.
            return;
        }

        frm.dashboard.set_indicator(__('Загрузка инженеров...'), 'blue');

        frappe.call({
            method: 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object',
            args: {
                service_object_name: frm.doc.service_object_link // Имя аргумента в Python-функции
            },
            callback: function(r) {
                frm.dashboard.clear_indicator();
                if (r.message && Array.isArray(r.message)) {
                    if (r.message.length > 0) {
                        frm.set_query(engineer_field, function() {
                            return {
                                filters: [
                                    ['User', 'name', 'in', r.message]
                                ]
                            };
                        });

                        // Если текущий выбранный инженер не входит в новый список, очищаем поле
                        if (frm.doc[engineer_field] && !r.message.includes(frm.doc[engineer_field])) {
                            frm.set_value(engineer_field, null);
                        }
                        // Опционально: если список инженеров содержит только одного, и поле не заполнено
                        else if (r.message.length === 1 && !frm.doc[engineer_field]) {
                            frm.set_value(engineer_field, r.message[0]);
                        }
                    } else {
                        // Инженеры не найдены
                        frm.set_query(engineer_field, function() {
                            return {
                                filters: [['User', 'name', 'in', ['NON_EXISTENT_USER_SO_LIST_IS_EMPTY']]]
                            };
                        });
                        frm.set_value(engineer_field, null);
                        frappe.show_alert({
                            message: __('Инженеры для данного объекта обслуживания не найдены.'),
                            indicator: 'info'
                        }, 5);
                    }
                } else {
                    // Некорректный ответ от сервера
                    frm.set_query(engineer_field, function() { return { filters: [['User', 'name', 'in', []]] }; });
                    frm.set_value(engineer_field, null);
                    frappe.show_alert({ message: __('Не удалось получить корректный список инженеров от сервера.'), indicator: 'warning' }, 7);
                }
                frm.refresh_field(engineer_field);
            },
            error: function(r) {
                frm.dashboard.clear_indicator();
                console.error("Ошибка при получении списка инженеров (общий JS): ", r);
                frm.set_query(engineer_field, null);
                frm.set_value(engineer_field, null);
                frm.refresh_field(engineer_field);
                frappe.show_alert({
                    message: __('Произошла ошибка при получении списка инженеров с сервера.'),
                    indicator: 'error'
                }, 7);
            }
        });
    },

    /**
     * Событие `refresh` вызывается при каждой перезагрузке формы.
     * Используется для настройки `add_fetch` и первоначального вызова логики фильтрации инженеров,
     * если объект обслуживания уже выбран в существующем документе.
     *
     * @param {object} frm - Объект текущей формы (Form).
     */
    refresh: function(frm) {
        // Настройка add_fetch для автоматического заполнения поля 'project'
        // из поля 'linked_service_project' связанного 'service_object_link'.
        // TODO: Verify fieldname 'service_object_link' in ServiceRequest (source Link field).
        // TODO: Verify fieldname 'linked_service_project' in ServiceObject (source field to fetch from).
        // TODO: Verify fieldname 'project' in ServiceRequest (target field).
        frm.add_fetch('service_object_link', 'linked_service_project', 'project');

        // Если service_object_link уже установлен при загрузке существующего документа,
        // и фильтр для инженеров еще не применялся (например, если этот скрипт только что добавлен),
        // вызываем обработчик service_object_link для применения фильтров.
        if (frm.doc.service_object_link && !frm.is_new()) {
            // Проверяем, был ли уже установлен query для поля инженера.
            // Это предотвращает лишний вызов, если query уже установлен (например, другим скриптом или ранее).
            // Однако, если мы хотим, чтобы этот скрипт всегда был главным, можно вызывать без проверки.
            const engineer_field = 'assigned_engineer'; // TODO: Verify fieldname
            if (frm.fields_dict[engineer_field] && !frm.fields_dict[engineer_field].get_query()) {
                 frm.trigger('service_object_link');
            }
        }
    }
});

/*
// --- АЛЬТЕРНАТИВНЫЙ ПОДХОД: ЕСЛИ ИНЖЕНЕРЫ В ДОЧЕРНЕЙ ТАБЛИЦЕ ---
// Этот блок актуален, если инженеры назначаются через дочернюю таблицу в ServiceRequest,
// а не через прямое Link поле 'assigned_engineer'.
// В этом случае, основная логика выше (для service_object_link и assigned_engineer) НЕ НУЖНА.
//
// frappe.ui.form.on('ServiceRequest', {
//     // TODO: Verify fieldname 'service_object_link'
//     service_object_link: function(frm) {
//         // TODO: Verify child table fieldname 'assigned_engineers_table'
//         if (frm.fields_dict['assigned_engineers_table']) {
//             frm.fields_dict['assigned_engineers_table'].grid.refresh();
//         }
//     },
//
//     refresh: function(frm) {
//         // TODO: Verify fieldnames: 'service_object_link', 'linked_service_project', 'project'
//         frm.add_fetch('service_object_link', 'linked_service_project', 'project');
//
//         // Фильтр для поля 'engineer' в дочерней таблице 'assigned_engineers_table'
//         // TODO: Verify child table fieldname 'assigned_engineers_table' and field 'engineer' in it.
//         // TODO: Verify python method path 'ferum_customs.utils.utils.get_engineers_for_service_object' (или аналогичный)
//         frm.set_query('engineer', 'assigned_engineers_table', function(doc, cdt, cdn) {
//             if (doc.service_object_link) {
//                 return {
//                     query: 'ferum_customs.utils.utils.get_engineers_for_service_object',
//                     filters: {
//                         service_object_name: doc.service_object_link // Имя аргумента в Python
//                     }
//                 };
//             }
//             return { filters: [['User', 'name', 'in', ['NON_EXISTENT_USER']]] };
//         });
//     }
// });
*/