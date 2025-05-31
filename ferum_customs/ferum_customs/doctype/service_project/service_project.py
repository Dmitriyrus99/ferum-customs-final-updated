"""Контроллер DocType *ServiceProject* – проект (совокупность заявок)."""

from __future__ import annotations

import frappe
from frappe.model.document import Document


class ServiceProject(Document):
    """Проект обслуживания клиентов."""

    def validate(self):
        """Проверяем, что дата окончания ≥ даты начала."""
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw("Дата окончания проекта меньше даты начала.")
