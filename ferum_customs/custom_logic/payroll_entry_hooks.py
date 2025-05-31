# ferum_customs/custom_logic/payroll_entry_hooks.py
"""Хуки для DocType *PayrollEntryCustom* (расширение штатного Payroll Entry)."""

from __future__ import annotations
from typing import TYPE_CHECKING

import frappe

if TYPE_CHECKING:
    from ..ferum_customs.doctype.payrollentrycustom.payroll_entry_custom import PayrollEntryCustom


def validate(doc: "payroll_entry_custom", method: str | None = None) -> None:
    """
    Демонстрационный пример – проверяем корректность периода.
    Args:
        doc: Экземпляр документа PayrollEntryCustom.
        method: Имя вызвавшего метода (например, "on_submit", "validate").
    """
    if doc.end_date and doc.start_date and doc.end_date < doc.start_date: # Ensure fields exist
        frappe.throw("Дата окончания не может быть раньше даты начала.")


def calculate_total_payable(doc: "payroll_entry_custom", method: str | None = None) -> None:
    """
    Рассчитывает итоговую сумму к выплате.
    Эта функция должна быть реализована для расчета `total_payable`.
    Например, на основе данных из Service Reports или других критериев.

    Args:
        doc: Экземпляр документа PayrollEntryCustom.
        method: Имя вызвавшего метода.
    """
    # FIXME: Implement logic to calculate total_payable
    # Example:
    # total_bonus = 0
    # service_reports = frappe.get_all("Service Report", filters={"employee": doc.employee, "payroll_period": doc.name}, fields=["bonus_amount"])
    # for report in service_reports:
    #     total_bonus += report.bonus_amount
    # doc.total_payable = (doc.base_salary or 0) + total_bonus - (doc.deductions or 0)
    frappe.msgprint(f"FIXME: Implement `calculate_total_payable` for PayrollEntryCustom '{doc.name}'")
    # For now, let's set it to 0 if not calculated
    if doc.total_payable is None:
         doc.total_payable = 0