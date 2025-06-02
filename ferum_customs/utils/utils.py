# ferum_customs/utils/utils.py
"""
Общие вспомогательные (utility) функции для приложения `ferum_customs`.

Эти функции могут быть вызваны из разных частей приложения,
включая хуки, серверные скрипты или другие утилиты.

Whitelisted-функции из этого модуля могут быть вызваны с клиента через `frappe.call`.
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional

import frappe
from frappe import _ # Для перевода строк

if TYPE_CHECKING:
    # Импортируем типы для DocTypes, если они используются в функциях
    # from ..doctype.service_object.service_object import ServiceObject
    from frappe.model.document import Document as FrappeDocument

# Пример whitelisted-функции, которая была предоставлена пользователем.
# Убедитесь, что эта функция действительно нужна и используется.
# Если она дублирует логику из service_request_hooks.get_engineers_for_object,
# возможно, стоит использовать одну из них и удалить дубликат.
@frappe.whitelist()
def get_engineers_for_service_object(service_object_name: str) -> List[str]:
    """
    Возвращает список User ID инженеров, назначенных на указанный объект обслуживания (ServiceObject).
    Эта функция предназначена для вызова с клиента или с сервера.

    Args:
        service_object_name: Имя (ID) объекта обслуживания (DocType ServiceObject).

    Returns:
        Список уникальных User ID инженеров. Пустой список, если инженеры не найдены,
        объект не существует или произошла ошибка.

    Raises:
        frappe.ValidationError: Если `service_object_name` не предоставлен.
        (косвенно) frappe.DoesNotExistError: Если ServiceObject не найден (через get_doc).
    """
    if not service_object_name:
        # Можно также вернуть пустой список и залогировать, вместо выброса исключения,
        # если клиентский скрипт ожидает список и может обработать пустой.
        frappe.throw(_("Имя объекта обслуживания (Service Object name) не может быть пустым."), exc=frappe.ValidationError)
        # return [] # Если предпочитаем не выбрасывать исключение

    engineers: List[str] = []
    try:
        # TODO: Verify DocType name 'ServiceObject' and child table fieldname 'assigned_engineers'
        # TODO: Verify fieldname 'engineer' in child table 'AssignedEngineerItem' (linked to User)
        if not frappe.db.exists("ServiceObject", service_object_name):
            frappe.logger(__name__).info(f"ServiceObject '{service_object_name}' not found in `get_engineers_for_service_object` from utils.")
            # frappe.msgprint(_("Объект обслуживания {0} не найден.").format(service_object_name)) # msgprint в whitelisted методе может быть не всегда уместен
            return []

        service_object_doc: "FrappeDocument" = frappe.get_doc("ServiceObject", service_object_name)
        
        assigned_engineers_table = service_object_doc.get("assigned_engineers")
        if assigned_engineers_table and isinstance(assigned_engineers_table, list):
            for item in assigned_engineers_table:
                if item.get("engineer"):
                    engineers.append(item.engineer)
        
        return list(set(engineers)) # Возвращаем уникальный список

    except frappe.DoesNotExistError: # Ловим конкретно от get_doc, если exists прошел, но что-то пошло не так
        frappe.logger(__name__).warning(
            f"ServiceObject '{service_object_name}' not found via get_doc, though it might exist (unexpected).",
            exc_info=True
        )
        return []
    except Exception as e:
        frappe.logger(__name__).error(
            f"Error fetching engineers for ServiceObject '{service_object_name}' in utils.get_engineers_for_service_object: {e}",
            exc_info=True
        )
        # Для клиентских вызовов лучше не выбрасывать общее исключение, а вернуть пустой список или специальный объект ошибки,
        # если клиент может его обработать. В данном случае возвращаем пустой список.
        return []

# --- Другие возможные утилиты ---

# def format_address(address_doc: "FrappeDocument", include_country: bool = True) -> str:
#     """
#     Форматирует адрес из документа типа Address в одну строку.
#     Args:
#         address_doc: Документ адреса (DocType Address).
#         include_country: Включать ли страну в отформатированную строку.
#     Returns:
#         Отформатированная строка адреса.
#     """
#     if not address_doc:
#         return ""
    
#     parts = [
#         address_doc.get("address_line1"),
#         address_doc.get("address_line2"),
#         address_doc.get("city"),
#         address_doc.get("state"),
#         address_doc.get("pincode"),
#     ]
#     if include_country and address_doc.get("country"):
#         parts.append(address_doc.get("country"))
        
#     return ", ".join(filter(None, parts))


# def get_default_currency() -> str:
#     """
#     Возвращает системную валюту по умолчанию.
#     """
#     return frappe.get_cached_value("Company", frappe.defaults.get_global_default("company"), "default_currency") or "USD"