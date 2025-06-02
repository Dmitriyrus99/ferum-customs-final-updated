// Предполагаемый путь: ferum_customs/public/js/ferum_customs/service_request.js (если build.json настроен так)
// или ferum_customs/ferum_customs/doctype/service_request/service_request.js (если это скрипт для конкретного DocType)
// Данный код предполагает, что это общий клиентский скрипт для формы ServiceRequest.

// Убедитесь, что Python-метод 
// 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object'
// добавлен в whitelist в hooks.py вашего приложения.

frappe.ui.form.on('ServiceRequest', {
    // Убедитесь, что 'service_object_link' - это корректное имя поля (типа Link) 
    // в DocType ServiceRequest, которое ссылается на ServiceObject.
    // Также убедитесь, что 'assigned_engineer' - это корректное имя поля (типа Link к User)
    // в DocType ServiceRequest, куда будет подставляться отфильтрованный инженер.
    // И поле 'project' (типа Link к ServiceProject) также существует.

    service_object_link: function(frm) {
        if (!frm.doc.service_object_link) {
            // Очищаем поля, зависимые от service_object_link
            frm.set_value('assigned_engineer', null); 
            frm.set_query('assigned_engineer', null); // Сбрасываем предыдущие фильтры для инженера
            
            // Если проект также зависит только от service_object_link (и не получается иначе)
            // frm.set_value('project', null); 
            // Однако, add_fetch обычно справляется с очисткой, если source-поле пустое.
            
            frm.refresh_fields(['assigned_engineer', 'project']);
            return;
        }

        frm.dashboard.set_indicator(__('Загрузка инженеров...'), 'blue');

        frappe.call({
            method: 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object',
            args: { 
                service_object_name: frm.doc.service_object_link // Передаем имя объекта
            },
            callback: function(r) {
                frm.dashboard.clear_indicator();
                if (r.message && Array.isArray(r.message)) {
                    if (r.message.length > 0) {
                        frm.set_query('assigned_engineer', function() {
                            return {
                                filters: [
                                    // Фильтруем пользователей по списку имен (ID)
                                    ['User', 'name', 'in', r.message]
                                ]
                            };
                        });
                        
                        // Опционально: если список инженеров содержит только одного, 
                        // и поле инженера еще не заполнено, можно его выбрать автоматически.
                        if (r.message.length === 1 && !frm.doc.assigned_engineer) {
                            frm.set_value('assigned_engineer', r.message[0]);
                        } else if (frm.doc.assigned_engineer && !r.message.includes(frm.doc.assigned_engineer)) {
                            // Если текущий выбранный инженер не входит в новый список, очищаем поле
                            frm.set_value('assigned_engineer', null);
                        }

                    } else {
                        // Инженеры не найдены для данного объекта обслуживания.
                        frm.set_query('assigned_engineer', function() {
                            return {
                                filters: [
                                    // Устанавливаем фильтр, который вернет пустой список
                                    ['User', 'name', 'in', ['NON_EXISTENT_USER_SO_LIST_IS_EMPTY']] 
                                ]
                            };
                        });
                        frm.set_value('assigned_engineer', null); // Очищаем значение, так как нет опций
                        frappe.show_alert({
                            message: __('Инженеры для данного объекта обслуживания не найдены.'), 
                            indicator: 'info'
                        }, 5); // Сообщение исчезнет через 5 секунд
                    }
                } else {
                     // Ответ не содержит ожидаемого списка или r.message не массив
                    frm.set_query('assigned_engineer', function() { return { filters: [['User', 'name', 'in', []]] }; });
                    frm.set_value('assigned_engineer', null);
                    frappe.show_alert({ 
                        message: __('Не удалось получить корректный список инженеров от сервера.'), 
                        indicator: 'warning' 
                    }, 7);
                }
                frm.refresh_field('assigned_engineer');
            },
            error: function(r) {
                frm.dashboard.clear_indicator();
                console.error("Ошибка при получении списка инженеров: ", r);
                // Сбрасываем фильтры и значение в случае ошибки
                frm.set_query('assigned_engineer', null); 
                frm.set_value('assigned_engineer', null);
                frm.refresh_field('assigned_engineer');
                frappe.show_alert({
                    message: __('Произошла ошибка при получении списка инженеров с сервера.'), 
                    indicator: 'error'
                }, 7);
            }
        });
    },

    refresh: function(frm) {
        // Настройка add_fetch при загрузке/обновлении формы.
        // Это заполнит поле 'project' в ServiceRequest
        // из поля 'linked_service_project' выбранного ServiceObject при изменении 'service_object_link'.
        // Убедитесь, что имена полей верны:
        //   - 'service_object_link' в ServiceRequest (поле Link на ServiceObject)
        //   - 'linked_service_project' в ServiceObject (поле Link на ServiceProject)
        //   - 'project' в ServiceRequest (поле Link на ServiceProject, куда будет записано значение)
        // TODO: Verify fieldnames: 'service_object_link', 'linked_service_project', 'project'
        frm.add_fetch('service_object_link', 'linked_service_project', 'project');

        // Если service_object_link уже установлен при загрузке существующего документа,
        // и список инженеров нужно отфильтровать сразу (например, если ранее не было клиентского скрипта).
        if (frm.doc.service_object_link && !frm.is_new()) {
             // Проверяем, нужно ли действительно вызывать триггер.
             // Это может быть излишним, если данные уже корректны или set_query сработает автоматически.
             // frm.trigger('service_object_link'); // Может вызвать повторный frappe.call
             // Лучше просто обновить фильтр, если он не был установлен ранее
             if (frm.get_field('assigned_engineer').get_query() === undefined) {
                frm.trigger('service_object_link');
             }
        }
    }
});

/*
// --- АЛЬТЕРНАТИВНЫЙ ПОДХОД ДЛЯ КЛИЕНТСКОГО СКРИПТА: ЕСЛИ ИНЖЕНЕРЫ В ДОЧЕРНЕЙ ТАБЛИЦЕ ---
// Этот блок нужно использовать ВМЕСТО обработчика `service_object_link` выше, 
// если у вас инженеры назначаются через дочернюю таблицу в ServiceRequest.
// 
// Предположим:
// - 'ServiceRequest' имеет дочернюю таблицу с fieldname 'assigned_engineers_table'.
// - В каждой строке 'assigned_engineers_table' есть поле Link к User с fieldname 'engineer'.
// - Python-метод 'ferum_customs.utils.get_engineers_for_service_object' существует,
//   добавлен в whitelist и возвращает список инженеров для frappe.utils. исполнителя запросов.

frappe.ui.form.on('ServiceRequest', {
    service_object_link: function(frm) {
        if (!frm.doc.service_object_link) {
            // Логика очистки для дочерней таблицы, если необходимо
            // Например, очистить поле 'engineer' во всех строках таблицы 'assigned_engineers_table'
            // и сбросить фильтры для этого поля.
            // Это может потребовать итерации по строкам грида и вызова set_query для каждой.
            if (frm.fields_dict['assigned_engineers_table']) { // TODO: Verify child table fieldname
                frm.fields_dict['assigned_engineers_table'].grid.df.fields.find(f => f.fieldname === 'engineer').get_query = null; // Сброс глобального query
                frm.fields_dict['assigned_engineers_table'].grid.refresh();
            }
            return;
        }
        // Обновляем грид, чтобы триггеры set_query сработали для существующих строк
        if (frm.fields_dict['assigned_engineers_table']) { // TODO: Verify child table fieldname
            frm.fields_dict['assigned_engineers_table'].grid.refresh();
        }
    },

    refresh: function(frm) {
        // TODO: Verify fieldnames: 'service_object_link', 'linked_service_project', 'project'
        frm.add_fetch('service_object_link', 'linked_service_project', 'project');

        // Фильтр для поля 'engineer' в дочерней таблице 'assigned_engineers_table'
        // Этот фильтр будет применяться ко всем строкам таблицы при их отображении/добавлении.
        // TODO: Verify child table fieldname 'assigned_engineers_table' and field 'engineer' in it.
        // TODO: Verify python method path 'ferum_customs.utils.get_engineers_for_service_object'
        frm.set_query('engineer', 'assigned_engineers_table', function(doc, cdt, cdn) {
            // doc - это ServiceRequest (родительский документ)
            // cdt, cdn - Child DocType и Child DocName (имя строки в дочерней таблице)
            if (doc.service_object_link) { 
                return {
                    query: 'ferum_customs.utils.get_engineers_for_service_object', 
                    filters: {
                        // 'service_object' - это имя аргумента в Python-функции get_engineers_for_service_object
                        service_object: doc.service_object_link 
                    }
                };
            }
            // Если service_object_link не указан, возвращаем пустой объект или фильтр, не дающий результатов
            return {
                filters: [['User', 'name', 'in', ['NON_EXISTENT_USER']]]
            }; 
        });
    }
});
*/