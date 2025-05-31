"""Контроллер *PayrollEntryCustom* – расширяет штатный Payroll Entry."""

from __future__ import annotations

from frappe.model.document import Document


class PayrollEntryCustom(Document):
    """Доп. поле для связи расчётного листа с ServiceReport."""
