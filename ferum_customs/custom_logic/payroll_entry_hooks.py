# ferum_customs/ferum_customs/custom_logic/payroll_entry_hooks.py
"""Хуки для DocType *PayrollEntryCustom* (расширение штатного Payroll Entry)."""

from __future__ import annotations
from typing import TYPE_CHECKING

import frappe
from frappe import _ # Для перевода строк

if TYPE_CHECKING:
    # Предполагаемая структура для импорта DocType:
    from ..doctype.payroll_entry_custom.payroll_entry_custom import PayrollEntryCustom
    # from ..doctype.service_report.service_report import ServiceReport # Если используется в расчетах

def validate(doc: "PayrollEntryCustom", method: str | None = None) -> None:
    """
    Проверяет корректность дат периода. Дата окончания не может быть раньше даты начала.
    
    Args:
        doc: Экземпляр документа PayrollEntryCustom.
        method: Имя вызвавшего метода (например, "on_submit", "validate").
    
    Raises:
        frappe.ValidationError: Если дата окончания раньше даты начала.
    """
    # TODO: Verify fieldnames 'start_date' and 'end_date' exist in PayrollEntryCustom DocType JSON
    if doc.get("start_date") and doc.get("end_date"):
        if doc.end_date < doc.start_date:
            frappe.throw(_("Дата окончания периода расчета ({0}) не может быть раньше даты начала ({1}).").format(
                frappe.utils.formatdate(doc.end_date), frappe.utils.formatdate(doc.start_date)
            ))
    
    # Сюда можно добавить другие проверки для PayrollEntryCustom.
    # if not doc.get("employee"):
    #     frappe.throw(_("Не выбран сотрудник для расчета зарплаты."))

def before_save(doc: "PayrollEntryCustom", method: str | None = None) -> None:
    """
    Рассчитывает итоговую сумму к выплате перед сохранением документа.
    Эта функция ДОЛЖНА БЫТЬ РЕАЛИЗОВАНА для расчета `total_payable`.
    Например, на основе данных из Service Reports или других критериев.

    Args:
        doc: Экземпляр документа PayrollEntryCustom.
        method: Имя вызвавшего метода (например, "on_submit", "before_save", "validate").
    """
    
    # FIXME: Требуется реализовать логику расчета `doc.total_payable`
    # Ниже приведен примерный каркас, который нужно адаптировать под вашу бизнес-логику.
    
    # frappe.logger(__name__).debug(f"Attempting to calculate total_payable for {doc.name}")

    # total_bonus_from_reports = 0.0
    # base_salary = doc.get("base_salary", 0.0) # TODO: Verify fieldname 'base_salary'
    # total_deduction = doc.get("total_deduction", 0.0) # TODO: Verify fieldname 'total_deduction'
    
    # if doc.employee and doc.start_date and doc.end_date:
    #     try:
    #         service_reports = frappe.get_all(
    #             "ServiceReport", # Используйте корректное имя DocType Service Report
    #             filters={
    #                 "employee": doc.employee, # TODO: Verify fieldname 'employee' in ServiceReport
    #                 "posting_date": ["between", [doc.start_date, doc.end_date]],
    #                 "docstatus": 1 # Обычно учитываются только подтвержденные отчеты
    #                 # Возможно, потребуется дополнительный фильтр, связывающий отчет с этим PayrollEntryCustom
    #                 # "custom_payroll_entry_ref": doc.name, 
    #             },
    #             fields=["custom_bonus_amount"] # TODO: Verify fieldname 'custom_bonus_amount' in ServiceReport
    #         )
    #         for report in service_reports:
    #             total_bonus_from_reports += report.get("custom_bonus_amount", 0.0)
            
    #         doc.total_payable = (base_salary + total_bonus_from_reports) - total_deduction
    #         frappe.logger(__name__).info(f"Calculated total_payable for {doc.name}: {doc.total_payable}")

    #     except Exception as e:
    #         frappe.logger(__name__).error(
    #             f"Error calculating total_payable for PayrollEntryCustom '{doc.name}': {e}",
    #             exc_info=True
    #         )
    #         # Можно решить, стоит ли прерывать сохранение или установить значение по умолчанию
    #         # frappe.throw(_("Ошибка при расчете итоговой суммы к выплате."))
    #         doc.total_payable = base_salary - total_deduction # Пример запасного варианта
    # else:
    #     # Если не хватает данных для расчета бонусов
    #     doc.total_payable = base_salary - total_deduction

    # Временное сообщение-заглушка для разработчика
    # Показываем сообщение один раз за сессию для этого документа, чтобы не спамить
    # TODO: Verify fieldname 'total_payable' exists in PayrollEntryCustom DocType JSON
    session_flag_key = f"developer_msg_payroll_calc_{doc.name or frappe.generate_hash()}" # generate_hash для новых доков
    if not frappe.flags.get(session_flag_key):
        frappe.msgprint(
            _("FIXME: Разработчик! Реализуйте функцию `before_save` (расчет `total_payable`) для документа '{0}' типа PayrollEntryCustom. Текущее значение: {1}").format(
                doc.name or _("Новый документ"), doc.get("total_payable", _("не установлено"))
            ),
            title=_("Задача для разработчика"),
            indicator="orange"
        )
        frappe.flags[session_flag_key] = True

    # Установка значения по умолчанию (0.0), если расчет не был выполнен или поле пустое.
    # Это важно, если `total_payable` - обязательное числовое поле.
    if doc.get("total_payable") is None:
        doc.total_payable = 0.0 # Используем float для денежных сумм

    # Округление до 2 знаков после запятой, если это денежная сумма
    if isinstance(doc.get("total_payable"), (float, int)):
        doc.total_payable = round(doc.total_payable, 2)