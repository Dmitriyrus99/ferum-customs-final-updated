"""Хуки для DocType *ServiceObject* – оборудование / объект обслуживания."""

from __future__ import annotations

import frappe


def validate(doc, *_):
    """Проверяем уникальность серийного номера объекта (пример бизнес-требования)."""
    if doc.serial_no and frappe.db.exists(
        "service_object", {"serial_no": doc.serial_no, "name": ("!=", doc.name)}
    ):
        frappe.throw(f"Серийный номер {doc.serial_no} уже используется другим объектом.")
