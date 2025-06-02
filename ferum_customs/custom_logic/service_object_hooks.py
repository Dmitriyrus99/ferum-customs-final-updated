# ferum_customs/ferum_customs/custom_logic/service_object_hooks.py
"""Хуки для DocType *ServiceObject* – оборудование / объект обслуживания."""

from __future__ import annotations
from typing import TYPE_CHECKING

import frappe
from frappe import _ # Для перевода строк

if TYPE_CHECKING:
    # Замените на актуальный путь к вашему DocType ServiceObject, если он определен.
    from ..doctype.service_object.service_object import ServiceObject
    # from frappe.model.document import Document # Общий тип для документов
    # ServiceObject = Document

def validate(doc: "ServiceObject", method: str | None = None) -> None:
    """
    Проверяет уникальность серийного номера объекта обслуживания.
    Эта проверка является примером бизнес-требования.

    Args:
        doc: Экземпляр документа ServiceObject.
        method: Имя вызвавшего метода (например, "validate").

    Raises:
        frappe.ValidationError: Если серийный номер не уникален.
    """
    # TODO: Verify fieldname 'serial_no' exists in ServiceObject DocType JSON
    if doc.get("serial_no"):
        # Удаляем возможные пробелы по краям перед проверкой
        serial_no_cleaned = doc.serial_no.strip()
        if not serial_no_cleaned: # Если после очистки строка пустая
            # Можно решить, считать ли это ошибкой или просто проигнорировать
            # frappe.throw(_("Серийный номер не может состоять только из пробелов."))
            return 

        # Формируем фильтры для поиска дубликатов.
        # Ищем ServiceObject с таким же serial_no, но с другим именем (doc.name).
        # Это гарантирует, что мы не найдем сам текущий документ при его редактировании.
        filters = {
            "serial_no": serial_no_cleaned,
            "name": ["!=", doc.name]
            # Можно добавить фильтр по компании, если серийные номера уникальны в рамках компании
            # "company": doc.company 
        }
        
        # frappe.db.exists возвращает имя существующего документа или None
        existing_doc_name = frappe.db.exists("ServiceObject", filters)

        if existing_doc_name:
            # Если дубликат найден, выбрасываем исключение с переводимым сообщением.
            error_message = _("Серийный номер '{0}' уже используется другим объектом обслуживания: {1}.").format(
                serial_no_cleaned, existing_doc_name
            )
            frappe.throw(error_message, title=_("Ошибка уникальности"))
            
    # Сюда можно добавить другие проверки для ServiceObject.
    # Например, проверка связанных полей, форматов и т.д.
    # if doc.installation_date and doc.installation_date > frappe.utils.today():
    #     frappe.throw(_("Дата установки не может быть в будущем."))