"""Контроллер DocType *ServiceObject* – объект оборудования."""

from __future__ import annotations

from frappe.model.document import Document


class ServiceObject(Document):
    """Оборудование клиента, подлежащее обслуживанию."""
