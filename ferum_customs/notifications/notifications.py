# ferum_customs/notifications/notifications.py
"""
Конфигурация уведомлений для приложения `ferum_customs`.

Эта функция `get_notification_config` должна быть указана в `hooks.py`:
`notification_config = "ferum_customs.notifications.notifications.get_notification_config"`

Возвращает словарь, описывающий условия для отправки стандартных уведомлений Frappe.
"""

from frappe import _ # Для перевода возможных строк в будущем

# Импорт констант для статусов, если они используются в условиях
from ..constants import STATUS_OTKRYTA, STATUS_V_RABOTE, ROLE_PROEKTNYJ_MENEDZHER

def get_notification_config() -> dict:
    """
    Возвращает конфигурацию для стандартных уведомлений Frappe.
    """
    return {
        "ServiceRequest": {
            # Условие для срабатывания уведомления:
            # Отправлять, когда ServiceRequest находится в одном из указанных статусов.
            "condition": f"doc.status in ['{STATUS_OTKRYTA}', '{STATUS_V_RABOTE}']",
            
            # Получатели:
            "send_to_roles": [ROLE_PROEKTNYJ_MENEDZHER],

            # Сообщение уведомления (можно использовать Jinja шаблонизацию)
            "subject": _("Обновление по Заявке на обслуживание: {{ doc.name }}"),
            "message": _("""
Уважаемый пользователь,

Информация по заявке на обслуживание <h3>{{ doc.name }}</h3>:
{% if doc.subject %}Тема: {{ doc.subject }} {% endif %}

Текущий статус: <strong>{{ doc.status }}</strong>.
{% if doc.custom_customer %}Клиент: {{ frappe.get_cached_value("Customer", doc.custom_customer, "customer_name") or doc.custom_customer }} {% endif %}
{% if doc.custom_service_object_link %}Объект обслуживания: {{ doc.custom_service_object_link }} {% endif %}
{% if doc.custom_assigned_engineer %}Назначенный инженер: {{ frappe.get_cached_value("User", doc.custom_assigned_engineer, "full_name") or doc.custom_assigned_engineer }} {% endif %}

Пожалуйста, просмотрите заявку: {{ frappe.utils.get_link_to_form('ServiceRequest', doc.name) }}

Спасибо.
""")
        },
        # "ServiceReport": { # Пример для другого DocType
        #     "condition": "doc.docstatus == 1", # Отправлять при отправке (submit) ServiceReport
        #     "send_to_roles": [ROLE_PROEKTNYJ_MENEDZHER],
        #     "subject": _("Отчет о выполненных работах {{ doc.name }} был отправлен"),
        #     "message": _("Отчет {{ doc.name }} для заявки {{ doc.service_request }} был отправлен.") # service_request - стандартное поле в ServiceReport
        # }
    }